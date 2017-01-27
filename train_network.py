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
parser.add_argument('--load', type=str, default='',
                    help='the file from which to load a pretrained model weights (optional, requires correct hyperparameters)')
parser.add_argument('--eval', action='store_true',
                    help='if present, calculate the fraction of successful corrections based on sampling the NN')
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
from codes import ToricCode
import numpy as np
import tqdm


f = np.load(args.trainset)
(Zstab_x_train, Zstab_y_train, Xstab_x_train, Xstab_y_train,
 Zstab_x_test,  Zstab_y_test,  Xstab_x_test,  Xstab_y_test) = [f['arr_%d'%_] for _ in range(8)]

model = create_model(L=args.dist,
                     hidden_sizes=args.layers,
                     hidden_act=args.hact,
                     act=args.act)
if args.load:
    model.load_weights(args.load)
if args.epochs:
    hist = model.fit(Zstab_x_train, Zstab_y_train,
                     nb_epoch=args.epochs,
                     batch_size=args.batch,
                     validation_data=(Zstab_x_test, Zstab_y_test)
                    )
    model.save_weights(args.out)
    with open(args.out+'.log', 'w') as f:
        f.write(str((hist.params, hist.history)))
if args.eval:
    L = args.dist
    H = ToricCode(L).flatXflips2Zstab
    E = ToricCode(L).flatXflips2Zerr
    c = 0.
    size = len(Zstab_y_test)
    for flips, stab in zip(tqdm.tqdm(Zstab_y_test), Zstab_x_test):
        pred = model.predict(np.array([stab])).ravel() # TODO those seem like unnecessary shape changes
        sample = pred>np.random.uniform(size=2*L**2)
        while np.any(stab!=H.dot(sample)%2):
            sample = pred>np.random.uniform(size=2*L**2)
        c += np.any(E.dot((sample+flips)%2)%2)
    with open(args.out+'.eval', 'w') as f:
        f.write('%.10f'%(1-c/size))
