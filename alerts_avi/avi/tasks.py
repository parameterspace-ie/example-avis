"""
GAVIP Example AVIS: Alerts AVI

AVI pipeline
"""

import os
# import datetime
import json
from django.conf import settings

# Class used for creating pipeline tasks
from pipeline.classes import (
    AviTask,
    AviParameter, AviLocalTarget,
)

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import mpld3
import json
import pandas


class AcquireData(AviTask):

    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'alerts_%s.csv' % self.outputFile
        ))

    def run(self):
        alertsurl = 'http://gsaweb.ast.cam.ac.uk/alerts/alerts.csv'
        alertsdata = pandas.read_csv(alertsurl, error_bad_lines=False)
        alertsdata.to_csv(self.output().path)


class PlotData(AviTask):

    outputFile = AviParameter()

    def output(self):
        # raise Exception(os.path.join(settings.OUTPUT_PATH, 'alerts_%s.dat' % self.outputFile))
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, '%s' % self.outputFile
        ))

    def requires(self):
        # Really weird error!!!
        # raise Exception('arse')
        # outputFile=self.outputFile
        return self.task_dependency(AcquireData)

    def run(self):

        # raise Exception('shite')

        # TODO: Pass DataFrame itself into task?
        # Pointless to read url, write to csv, then read csv

        alertsdata = pandas.read_csv(self.input().path)

        alertsdata.columns = [x.replace('#','').strip().lower() for x in alertsdata.columns.values.tolist()]

        # print alertsdata.ix[0,:]

        # TODO tidy DataFrame headers
        ra = np.array(alertsdata['radeg'])
        dec = np.array(alertsdata['decdeg'])
        mag = np.array(alertsdata['alertmag'])
        alclass = np.array(alertsdata['class'])

        cmap = mpl.cm.rainbow
        classes = list(set(alclass))
        colours = {classes[i]: cmap(i / float(len(classes))) for i in range(len(classes))}

        fig = plt.figure()
        # ax = fig.add_subplot(111)
        for i in range(len(ra)):
            plt.plot(ra[i], dec[i], 'o', ms=self.magtopoint(mag[i], mag), color=colours[alclass[i]])
        plt.xlabel('Right Ascension')
        plt.ylabel('Declination')

        # dots = []
        # labels = []
        # for i in range(len(classes)):
        #     dots.append(mpatches.Patch(color=colours[classes[i]]))
        #     labels.append(classes[i])


        # mpld3.save_html(fig, os.path.join(settings.OUTPUT_PATH, 'alerts_' + str(self.outputFile) + '.dat'))
        # mpld3.save_html(fig, os.path.join(settings.OUTPUT_PATH, 'alerts_' + str(234573) + '.dat'))
        # mpld3.save_html(fig, str(self.output().path))

        with open(self.output().path, 'w') as out:
            json.dump(mpld3.fig_to_dict(fig), out)

    def magtopoint(self, magval, mag):
        mx = mag.max()
        mn = mag.min()
        px = 10
        pn = 4
        pointsize = ((mx - magval) / (mx - mn)) * (px - pn) + pn
        return pointsize