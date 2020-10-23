import os
import tensorflow as tf

from models.punctuation_restoration_model import PunctuationRestorationModel
from utils.data_utils import split_to_batches
from utils.punctuation_preprocess import process_data

# dataset parameters
tf.flags.DEFINE_string("raw_path", "data/raw/LREC_converted", "path to raw dataset")
tf.flags.DEFINE_string("save_path", "data/dataset/lrec", "path to save dataset")
tf.flags.DEFINE_string("glove_name", "840B", "glove embedding name")

# glove word embedding
tf.flags.DEFINE_string("glove_path", "data/external/embeddings/glove.{}.{}d.txt", "glove embedding path")
tf.flags.DEFINE_integer("max_vocab_size", 50000, "maximal vocabulary size")
tf.flags.DEFINE_integer("max_sequence_len", 200, "maximal sequence length allowed")
tf.flags.DEFINE_integer("min_word_count", 1, "minimal word count in word vocabulary")

# dataset for train, validation and test
tf.flags.DEFINE_string("vocab", "data/dataset/lrec/vocab.json", "path to the word and tag vocabularies")
tf.flags.DEFINE_string("train_word_counter", "data/dataset/lrec/train_word_counter.json", "path to the word counter "
                                                                                          "in training datasets")
tf.flags.DEFINE_string("train_punct_counter", "data/dataset/lrec/train_punct_counter.json", "path to the punctuation "
                                                                                            "counter in traning "
                                                                                            "datasets")
tf.flags.DEFINE_string("dev_word_counter", "data/dataset/lrec/dev_word_counter.json", "path to the word counter in "
                                                                                      "development datasets")
tf.flags.DEFINE_string("dev_punct_counter", "data/dataset/lrec/dev_punct_counter.json", "path to the punctuation "
                                                                                        "counter in development "
                                                                                        "datasets")
tf.flags.DEFINE_string("ref_word_counter", "data/dataset/lrec/ref_word_counter.json", "path to the word counter in "
                                                                                      "ref test datasets")
tf.flags.DEFINE_string("ref_punct_counter", "data/dataset/lrec/ref_punct_counter.json", "path to the punctuation "
                                                                                        "counter in ref test datasets")
tf.flags.DEFINE_string("asr_word_counter", "data/dataset/lrec/asr_word_counter.json", "path to the word counter in "
                                                                                      "asr test datasets")
tf.flags.DEFINE_string("asr_punct_counter", "data/dataset/lrec/asr_punct_counter.json", "path to the punctuation "
                                                                                        "counter in asr test datasets")
tf.flags.DEFINE_string("train_set", "data/dataset/lrec/train.json", "path to the training datasets")
tf.flags.DEFINE_string("dev_set", "data/dataset/lrec/dev.json", "path to the development datasets")
tf.flags.DEFINE_string("dev_text", "data/raw/LREC_converted/dev.txt", "path to the development text")
tf.flags.DEFINE_string("ref_set", "data/dataset/lrec/ref.json", "path to the ref test datasets")
tf.flags.DEFINE_string("ref_text", "data/raw/LREC_converted/ref.txt", "path to the ref text")
tf.flags.DEFINE_string("asr_set", "data/dataset/lrec/asr.json", "path to the asr test datasets")
tf.flags.DEFINE_string("asr_text", "data/raw/LREC_converted/asr.txt", "path to the asr text")
tf.flags.DEFINE_string("pretrained_emb", "data/dataset/lrec/glove_emb.npz", "pretrained embeddings")

# network parameters
tf.flags.DEFINE_string("cell_type", "lstm", "RNN cell for encoder and decoder: [lstm | gru], default: lstm")
tf.flags.DEFINE_integer("num_layers", 4, "number of rnn layers")
tf.flags.DEFINE_multi_integer("num_units_list", [50, 50, 50, 300], "number of units for each rnn layer")
tf.flags.DEFINE_boolean("use_pretrained", True, "use pretrained word embedding")
tf.flags.DEFINE_boolean("tuning_emb", False, "tune pretrained word embedding while training")
tf.flags.DEFINE_integer("emb_dim", 300, "embedding dimension for encoder and decoder input words/tokens")
tf.flags.DEFINE_boolean("use_highway", True, "use highway network")
tf.flags.DEFINE_integer("highway_layers", 2, "number of layers for highway network")
tf.flags.DEFINE_boolean("use_crf", True, "use CRF decoder")

# training parameters
tf.flags.DEFINE_float("lr", 0.001, "learning rate")
tf.flags.DEFINE_string("optimizer", "adam", "optimizer: [adagrad | sgd | rmsprop | adadelta | adam], default: adam")
tf.flags.DEFINE_boolean("use_lr_decay", True, "apply learning rate decay for each epoch")
tf.flags.DEFINE_float("lr_decay", 0.05, "learning rate decay factor")
tf.flags.DEFINE_float("l2_reg", None, "L2 norm regularization")
tf.flags.DEFINE_float("minimal_lr", 1e-5, "minimal learning rate")
tf.flags.DEFINE_float("grad_clip", 2.0, "maximal gradient norm")
tf.flags.DEFINE_float("keep_prob", 0.75, "dropout keep probability for embedding while training")
tf.flags.DEFINE_integer("batch_size", 32, "batch size")
tf.flags.DEFINE_integer("epochs", 5, "train epochs")
tf.flags.DEFINE_integer("max_to_keep", 3, "maximum trained models to be saved")
tf.flags.DEFINE_integer("no_imprv_tolerance", 10, "no improvement tolerance")
tf.flags.DEFINE_string("checkpoint_path", "ckpt/punctuator/", "path to save models checkpoints")
tf.flags.DEFINE_string("summary_path", "ckpt/punctuator/summary/", "path to save summaries")
tf.flags.DEFINE_string("model_name", "punctuation_restoration_model", "models name")

# convert parameters to dict
config = tf.flags.FLAGS.flag_values_dict()

# preprocess data from raw data files
if not os.path.exists(config["save_path"]) or not os.listdir(config["save_path"]):
    process_data(config)
if not os.path.exists(config["pretrained_emb"]) and config["use_pretrained"]:
    process_data(config)

print("Load datasets...")
# used for training
train_set = split_to_batches(config["train_set"], config["batch_size"], shuffle=True)
# used for computing validate loss
valid_data = split_to_batches(config["dev_set"], config["batch_size"], shuffle=True)[0]
valid_text = config["dev_text"]
# used for evaluation metrics
test_texts = [config["ref_text"], config["asr_text"]]

print("Build models...")
model = PunctuationRestorationModel(config)

# if the model is already trained, you can restore the model here
# model.restore_last_session()

model.train(train_set, valid_data, valid_text, test_texts)

# sentence = 'this is a string of text with no punctuation this is a new sentence'
# print(model.inference(sentence))
