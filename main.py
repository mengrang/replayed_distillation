# python main.py --run_name=hinton800_mnist --dataset=mnist --model=hinton800 --procedure=train

import numpy as np
import tensorflow as tf
import datetime as dt

import models as m
import datasets as d
import utils as u
import procedures as p

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('run_name', '', 'The name of the experimental run')
flags.DEFINE_string('summary_folder', 'summaries/', 'Folder to save summaries, logs, stats, optimized_datasets')
flags.DEFINE_string('log_file', 'log.json', 'Default filename for logs saving')

flags.DEFINE_string('commit', '', '[OPTIONAL] commit hash for current experiment')
flags.DEFINE_string('dataset', '', 'mnist, mnist_conv, or the path to an optimized dataset.')
flags.DEFINE_string('model', '', 'hinton1200, hinton800, lenet, lenet_half, vgg19, vgg16')
flags.DEFINE_integer('rng_seed', 42, 'RNG seed, fixed for consistency')
flags.DEFINE_string('procedure', '', 'train, compute_stats, optimize_dataset, distill')
flags.DEFINE_string('loss', 'xent', 'xent, mse, or attrxent')
flags.DEFINE_string('lr', '0.001', 'learning rate')

flags.DEFINE_integer('epochs', 10, 'Number of training epochs')
flags.DEFINE_integer('train_batch_size', 64, 'number of examples to be used for training')
flags.DEFINE_integer('test_batch_size', 64, 'number of examples to be used for testing')
flags.DEFINE_integer('eval_interval', 100, 'Number of training steps between test set evaluations')
flags.DEFINE_integer('checkpoint_interval', 1000, 'Number of steps between checkpoints')

# the following are only used when loading a pre-trained model
# (e.g.: compute_stats, optimize, and distill)
flags.DEFINE_string('model_meta', '', 'The meta graphdef file for the saved model to be loaded.')
# e.g.: summaries/test_train_works/checkpoint/hinton1200-8000.meta
flags.DEFINE_string('model_checkpoint', '', 'The checkpoint to restore the graph from.')
# e.g.: summaries/test_train_works/checkpoint/hinton1200-8000

# the following is only used when computing statistics. graphwise_stats are
# computationaly expensive, and are only needed for spectral
# optimization_objectives, so we only compute them when the flag is set.
flags.DEFINE_boolean('compute_graphwise_stats', False, 'Whether to compute graphwise statistics (needed for spectral optimization objectives)')

# the following is only used for when optimizing a new dataset
flags.DEFINE_string('optimization_objective', '', 'top_layer, all_layers, all_layers_dropout, spectral_all_layers, spectral_layer_pairs')

# the following is only used for when distilling a model. --dataset should be
# the reconstructed/optimized dataset location (or the original dataset in the
# case of vanilla knowledge distillation), and --eval_dataset should be the
# original dataset (if available).
flags.DEFINE_string('eval_dataset', '', 'The dataset used to evaluate the model when distilling.')
# also when distilling a model, a student model needs to be specified. This
# will be trained from scratch using the output from the teacher as labels.
# the teacher needs to be --model and --model_meta/--model_checkpoint.
flags.DEFINE_string('student_model', '', 'The model to compress the teacher model into when distilling')


if __name__ == '__main__':
    # initial bookkeeping
    log = u.get_logger(FLAGS)
    np.random.seed(FLAGS.rng_seed)
    tf.set_random_seed(FLAGS.rng_seed)

    # initialize session
    sess = tf.Session(config=u.get_sess_config(use_gpu=True))

    # initialize dataset interface
    data = d.get(FLAGS.dataset, FLAGS)

    # run procedure (this will create and train graphs, etc).
    p.get(FLAGS.procedure).run(sess, FLAGS, data)

    # save log
    u.save_log(log, FLAGS.summary_folder, FLAGS.run_name, FLAGS.log_file)

