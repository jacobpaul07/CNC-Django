from django.test import TestCase

# Create your tests here.
import progressbar
from time import sleep
bar = progressbar.ProgressBar(maxval=20,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()
for i in range(20):
    bar.update(i+1)
    sleep(10)
bar.finish()