from fastai.imports import torch
from fastai.vision import load_learner, defaults, open_image

defaults.device = torch.device('cpu')


# print(torch.__version__)
# print(torchvision.__version__)
# print(fastai.__version__)

def analyze_image_meme(filename):
    learn = load_learner('neuro/meme')
    img = open_image(filename)
    pred_class, pred_idx, outputs = learn.predict(img)

    pred = sorted(
        zip(learn.data.classes, map(float, outputs)),
        key=lambda p: p[1],
        reverse=True
    )
    return pred_class, pred[:2]


def analyze_image_lion(filename):
    learn = load_learner('neuro/lions')
    img = open_image(filename)
    pred_class, pred_idx, outputs = learn.predict(img)

    pred = sorted(
        zip(learn.data.classes, map(float, outputs)),
        key=lambda p: p[1],
        reverse=True
    )
    return pred_class, pred[:2]


def analyze_image_dog(filename):
    learn = load_learner('neuro/cat_dogs')
    img = open_image(filename)
    pred_class, pred_idx, outputs = learn.predict(img)

    pred = sorted(
        zip(learn.data.classes, map(float, outputs)),
        key=lambda p: p[1],
        reverse=True
    )
    return pred_class, pred[:2]

# print(fastai.__version__)
# print(analyze_image('static/img/avatars/coolstalin.jpg'))
