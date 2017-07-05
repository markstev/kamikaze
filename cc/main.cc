#include <atomic>
#include <chrono>
#include <condition_variable>
#include <ctime>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

//#define USE_CUDA 1
#ifdef USE_CUDA
#include <opencv2/cudaobjdetect.hpp>
#endif
#include <opencv2/opencv.hpp>

constexpr char kFaceCascadeFile[] =
    "../haarcascades/haarcascade_frontalface_default.xml";
constexpr char kEyeCascadeFile[] = "../haarcascades/haarcascade_eye.xml";
constexpr char kMouthCascadeFile[] = "../haarcascades/haarcascade_smile.xml";
static constexpr int kWebcam = 0;
static const cv::Size kMinFaceSize(20, 20);

#define FIND_EYES 0

static const cv::Scalar kBlue(255, 0, 0);
static const cv::Scalar kGreen(0, 255, 0);
static const cv::Scalar kRed(0, 0, 255);
static const cv::Scalar kTeal(255, 255, 0);
static const cv::Scalar kYellow(0, 255, 255);
static const cv::Scalar kWhite(255, 255, 255);

cv::Size operator/(cv::Size s, int d) {
  s.width /= d;
  s.height /= d;
  return s;
}

cv::Point operator+(cv::Point p, cv::Size s) {
  p.x += s.width;
  p.y += s.height;
  return p;
}

enum class Action { LEFT, RIGHT, DOWN, UP };

std::ostream &operator<<(std::ostream &os, Action action) {
  const char *kActionNames[] = {"LEFT", "RIGHT", "DOWN", "UP"};
  return os << kActionNames[int(action)];
}

struct NoAssertHelper {};

struct AssertHelper {
  ~AssertHelper() { abort(); }

  operator NoAssertHelper() const { return NoAssertHelper(); }
};

template <typename T>
const AssertHelper &operator<<(const AssertHelper &helper, T &&msg) {
  std::cerr << std::forward<T>(msg);
  return helper;
}

#define ASSERT(cond)                                                           \
  ((cond)) ? NoAssertHelper() : AssertHelper() << __FILE__ << ":" << __LINE__  \
                                               << ": " << #cond

class Robot {
public:
  virtual ~Robot() {}
  virtual void operator()(Action action) = 0;
};

class NoOpRobot : public Robot {
public:
  void operator()(Action) final {}
};

class Recognizer {
public:
#ifdef USE_CUDA
  using Mat = cv::cuda::GpuMat;
#else
  using Mat = cv::Mat;
#endif

  Recognizer(Robot *robot) : robot_(robot) {
#ifndef USE_CUDA
    ASSERT(face_detector_->load(kFaceCascadeFile)) << " error loading "
                                                  << kFaceCascadeFile;
    ASSERT(eye_detector_->load(kEyeCascadeFile)) << " error loading "
                                                << kEyeCascadeFile;
    ASSERT(mouth_detector_->load(kMouthCascadeFile)) << " error loading "
                                                    << kMouthCascadeFile;
#endif
  }

  static void PlotFeature(cv::Mat &mat, const cv::Rect &feature,
                          const cv::Scalar &color) {
    cv::rectangle(mat, feature.tl(), feature.br(), color);
  }

  static cv::Rect GuessMouthLocation(const cv::Rect &face) {
    return cv::Rect(
        cv::Point(face.x + face.width / 4, face.y + 9 * face.height / 12),
        cv::Size(face.width / 2, face.height / 6));
  }

  static cv::Rect BestMouth(const std::vector<cv::Rect> &mouths) {
    cv::Rect best = mouths[0];
    for (const cv::Rect &mouth : mouths)
      if (mouth.width * mouth.height > best.width * best.height)
        best = mouth;
    return best;
  }

  static cv::Point MouthCenter(const cv::Rect &mouth) {
    return mouth.tl() + mouth.size() / 2;
  }

  static std::vector<Action> DetermineAction(cv::Mat &input_img,
                                             const cv::Point &mouth) {
    constexpr int kTargetSize = 20;
    const cv::Rect target(cv::Point((input_img.cols - kTargetSize) / 2,
                                    (input_img.rows - kTargetSize) / 2),
                          cv::Size(kTargetSize, kTargetSize));
    PlotFeature(input_img, target, kTeal);
    std::vector<Action> actions;
    if (mouth.x < target.x)
      actions.push_back(Action::LEFT);
    else if (mouth.x > target.x + target.width)
      actions.push_back(Action::RIGHT);
    if (mouth.y < target.y)
      actions.push_back(Action::UP);
    else if (mouth.y > target.y + target.height)
      actions.push_back(Action::DOWN);
    return actions;
  }

#ifdef USE_CUDA
  std::vector<cv::Rect> DetectMultiScale(cv::cuda::CascadeClassifier *cc,
                                         const cv::cuda::GpuMat &mat,
                                         double scale_factor = 1.3,
                                         int min_neighbors = 3,
                                         cv::Size min_size = {0, 0}) {
    std::vector<cv::Rect> rects;
    cv::cuda::GpuMat found;
    cc->setScaleFactor(scale_factor);
    cc->setMinNeighbors(min_neighbors);
    cc->setMinObjectSize(min_size);
    cc->detectMultiScale(mat, found);
    cc->convert(found, rects);
    return rects;
  }
#endif

  std::vector<cv::Rect> DetectMultiScale(cv::CascadeClassifier *cc,
                                         const cv::Mat &mat,
                                         double scale_factor = 1.3,
                                         int min_neighbors = 3,
                                         cv::Size min_size = {0, 0}) {
    std::vector<cv::Rect> rects;
    cc->detectMultiScale(mat, rects, scale_factor, min_neighbors, /*flags=*/0,
                         /*minSize=*/min_size);
    return rects;
  }

  void Detect(cv::Mat &input_img) {
    // cv::Mat gray;
    cv::cvtColor(input_img, gray_, cv::COLOR_BGR2GRAY);
    // gray_ = gray;
    auto start_time = std::chrono::high_resolution_clock::now();
    std::ostringstream action_str;
    for (auto &face :
         DetectMultiScale(face_detector_.get(), gray_, 1.3, 5, kMinFaceSize)) {
      PlotFeature(input_img, face, kBlue);
      PlotFeature(input_img, GuessMouthLocation(face), kYellow);
      if (FIND_EYES) {
        for (cv::Rect &eye :
             DetectMultiScale(eye_detector_.get(), gray_(face))) {
          eye += face.tl();
          PlotFeature(input_img, eye, kGreen);
        }
      }
      const cv::Rect mouth_roi(cv::Point(face.x, face.y + 2 * face.height / 3),
                               cv::Size(face.width, face.height / 3));
      std::vector<cv::Rect> mouths =
          DetectMultiScale(mouth_detector_.get(), gray_(mouth_roi));
      for (cv::Rect &mouth : mouths) { // Convert mouths to img space.
        mouth += mouth_roi.tl();
        PlotFeature(input_img, mouth, kRed);
      }
      if (mouths.empty()) {
        mouths.push_back(GuessMouthLocation(face));
      }
      for (Action action :
           DetermineAction(input_img, MouthCenter(BestMouth(mouths)))) {
        (*robot_)(action);
        action_str << action << " ";
      }
      break;
    }
    auto end_time = std::chrono::high_resolution_clock::now();
    std::ostringstream duration_str;
    duration_str << (std::chrono::duration<float>(1) / (end_time - start_time))
                 << " fps";
    cv::putText(input_img, duration_str.str(), cv::Point(0, 20),
                cv::FONT_HERSHEY_PLAIN, 1, kWhite);
    cv::putText(input_img, action_str.str(), cv::Point(0, 40),
                cv::FONT_HERSHEY_PLAIN, 2, kWhite);
    cv::imshow("img", input_img);
  }

private:
  Mat img_;
  Mat gray_;
  Robot *robot_;
#ifdef USE_CUDA
  cv::Ptr<cv::cuda::CascadeClassifier> face_detector_ =
      cv::cuda::CascadeClassifier::create(kFaceCascadeFile);
  cv::Ptr<cv::cuda::CascadeClassifier> eye_detector_ =
      cv::cuda::CascadeClassifier::create(kEyeCascadeFile);
  cv::Ptr<cv::cuda::CascadeClassifier> mouth_detector_ =
      cv::cuda::CascadeClassifier::create(kMouthCascadeFile);
#else
  std::unique_ptr<cv::CascadeClassifier> face_detector_{
      new cv::CascadeClassifier};
  std::unique_ptr<cv::CascadeClassifier> eye_detector_{
      new cv::CascadeClassifier};
  std::unique_ptr<cv::CascadeClassifier> mouth_detector_{
      new cv::CascadeClassifier};
#endif
};

void DetectImages(Recognizer *recognizer, int argc, char **argv) {
  cv::Mat image;
  for (int i = 0; i < argc; ++i) {
    std::cout << "=== " << argv[i] << std::endl;
    image = cv::imread(argv[i], 1);
    if (!image.data) {
      std::cerr << "error reading image " << argv[i] << std::endl;
      continue;
    }
    recognizer->Detect(image);
    if (cv::waitKey(0) == 'q')
      break;
  }
}

void DetectWebcam(Recognizer *recognizer) {
  std::mutex mu;
  std::condition_variable latest_image_cv;
  cv::Mat latest_image;
  std::atomic<bool> done(false);
  bool latest_image_ready = false;

  std::thread capture_thread([&] {
    cv::VideoCapture capture(kWebcam);
    while (!done.load(std::memory_order_relaxed)) {
      cv::Mat image;
      if (!capture.read(image)) {
        std::cerr << "error reading from webcam " << kWebcam << std::endl;
      } else {
        std::unique_lock<std::mutex> lock(mu);
        latest_image = image;
        latest_image_ready = true;
        lock.unlock();
        latest_image_cv.notify_one();
      }
    }
  });

  std::thread detect_thread([&] {
    cv::Mat image;
    for (int key = 0; key != 'q';) {
      {
        std::unique_lock<std::mutex> lock(mu);
        latest_image_cv.wait(lock, [&] { return latest_image_ready; });
        image = latest_image;
        latest_image_ready = false;
      }
      recognizer->Detect(image);
      key = cv::waitKey(1000 / 30);
      while (key == 'p')
        key = cv::waitKey(0); // Wait for another key to be pressed.
    }
    done = true;
  });

  detect_thread.join();
  capture_thread.join();
}

int main(int argc, char **argv) {
  NoOpRobot robot;
  Recognizer recognizer(&robot);
  if (argc == 1) {
    DetectWebcam(&recognizer);
  } else {
    DetectImages(&recognizer, argc - 1, argv + 1);
  }
  return 0;
}
