import argparse

parser = argparse.ArgumentParser(description='Train a neural network to decode a code.',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='''\
''')
parser.add_argument('dist', type=int,
                    help='the distance of the code')
parser.add_argument('trainset', type=str,
                    help='the name of the training set file (generated by `generate_training_data.py`)')
parser.add_argument('out', type=str,
                    help='the name of the output file (used as a prefix for the log file as well)')
parser.add_argument('--batch', type=int, default=32,
                    help='the batch size (default: %(default)s)')
parser.add_argument('--epochs', type=int, default=3,
                    help='the number of epochs (default: %(default)s)')
parser.add_argument('--hact', type=str, default='tanh',
                    help='the activation for hidden layers (default: %(default)s)')
parser.add_argument('--act', type=str, default='sigmoid',
                    help='the activation for the output layer (default: %(default)s)')
parser.add_argument('--layers', type=float, default=[4], nargs='+',
                    help='the list of sizes of the hidden layers (as a factor of the input layer) (default: %(default)s)')

args = parser.parse_args()
print(args)

from neural import create_model
import numpy as np

f = np.load(args.trainset)
(Zstab_x_train, Zstab_y_train, Xstab_x_train, Xstab_y_train,
 Zstab_x_test,  Zstab_y_test,  Xstab_x_test,  Xstab_y_test) = [f['arr_%d'%_] for _ in range(8)]

model = create_model(L=args.dist,
                     hidden_sizes=args.layers,
                     hidden_act=args.hact,
                     act=args.act)
hist = model.fit(Zstab_x_train, Zstab_y_train,
                 nb_epoch=args.epochs,
                 batch_size=args.batch,
                 validation_data=(Zstab_x_test, Zstab_y_test)
                )
model.save_weights(args.out)
with open(args.out+'.log', 'w') as f:
    f.write(str((hist.params, hist.history)))
