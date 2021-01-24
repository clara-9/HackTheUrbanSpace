from fastai.learner import load_learner


class Model:
    def __init__(self, path):
        self.learn = load_learner(path)
        classes = self.learn.dls.vocab

    def predict_single_image(self, img_file):
        prediction = self.learn.predict(img_file)
        return prediction
