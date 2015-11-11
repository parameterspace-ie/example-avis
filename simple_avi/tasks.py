import os
import time
from django.conf import settings

# Class used for creating pipeline tasks
from pipeline.classes import (
    AviTask,
    AviParameter, AviLocalTarget,
)

# CONNECTOR Library used for getting GACS data
from connectors import tapquery
import services.gacs as svc_gacs

# Library used for VOTable parsing
from astropy.io.votable import parse
# Libraries used for Bokeh plotting
from bokeh.resources import INLINE
from bokeh.plotting import figure
from bokeh.embed import file_html


class DummyTask(AviTask):
    """
    This is a sample task which has no dependencies. It only exists to further demonstrate dependency creation.
    """
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'dummyData_%s.vot' % self.outputFile
        ))

    def run(self):
        time.sleep(3)
        with open(self.output().path, "w") as outFile:
            outFile.write("dummyStuff")


class DownloadData(svc_gacs.GacsQuery):
    """
    This task uses an AVI service, to obtain a data product from GACS.
    Notice that we do not define a 'run' function! It is defined by the 
    service class which we extend.

    See :class:`GacsQuery`
    """
    query = AviParameter()
    output_file = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, 'simulatedData_%s.vot' % self.output_file
        ))

    def requires(self):
        return self.task_dependency(DummyTask, [self.output_file])


class ProcessData(AviTask):
    """
    This function requires a DownloadData class to be run. 
    We will obtain GACS data in this way.

    Once we have this data, we parse the VOTable. Then we 
    plot it using Bokeh.
    """
    query = AviParameter()
    outputFile = AviParameter()

    def output(self):
        return AviLocalTarget(os.path.join(
            settings.OUTPUT_PATH, self.outputFile
        ))

    def requires(self):
        return self.task_dependency(DownloadData, [self.query, self.outputFile])

    def run(self):
        # load the votable content from previous task
        votable = parse(self.input().path)
        data_arr = votable.get_first_table().array
        # Extract plot data
        mass = data_arr['mass']
        orbit_period = data_arr['orbit_period']
        # Create the bokeh plot
        p = figure(title="GACS scatter",
                   plot_width=600, plot_height=600
                   )
        p.scatter(mass, orbit_period,
                  size=3,
                  fill_alpha=0.5,
                  line_color="#6666ee",
                  fill_color="#ee6666",
                  )
        # Style the bokeh plot
        p.title_text_color = "green"
        p.title_text_font = "times"
        p.xaxis.axis_label = 'Solar Mass'
        p.yaxis.axis_label = 'Orbital Period'
        # Generate the HTML content and write it to the output file for this
        # task
        html = file_html(p, INLINE, "my plot")
        with open(self.output().path, 'w') as out:
            out.write(html)
