#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import sys
from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore
from os import listdir
from os.path import isfile, join
from operator import itemgetter, attrgetter

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<h1>Exports</h1>')
        path = './data/'
        files = groupFiles(path);

        self.response.write('<h3>' + str(len(files.keys())) + ' export(s) found in ' + path + '<br/> Click on the export name below to start the process, depending on the export size this process can take a very long time.</h3>')

        lst = '<ul>'

        for ename in files.keys():
            lst += '<a href="/export/' + ename + '">' 
            lst += '<li>' + ename + ' ('+ str(len(files[ename]))+' files)</li>' 
            lst += '</a>'

        lst += '</ul>'

        self.response.write(lst)

class ExportHandler(webapp2.RequestHandler):
    def get(self, ename):
        path = './data/'
        files = groupFiles(path)
        files = files[ename]

        #convert the file id to an int
        for v in files:
            v[3] = int(v[3])

        #sort by file id (index:3)
        files = sorted(files, key=itemgetter(3))
        rows = []
        for f in files:
            filename = path + f[6]
            raw = open(filename, 'r')
            reader = records.RecordsReader(raw)
            for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity = datastore.Entity.FromPb(entity_proto)
                header = []
                row = []
                for k,v in entity.items():
                    header.append(k)
                    row.append(v)
                rows.append(row)


        self.response.headers['Content-Type'] = 'text/csv';
        self.response.headers['Content-Disposition'] = str('attachment; filename="export.csv"');

        self.response.write(join(header) + "\n")
        for row in rows:
            self.response.write(join(row) + "\n")

def groupFiles(path):
    "processes the path and returns all data files grouped by export name"
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
    files = {}
    for f in onlyfiles:
        if f.find('.') == -1:
            split = f.split('-')
            if split[0] not in files:
                files[split[0]] = []
            split.append(f)
            files[split[0]].append(split)
    return files

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/export/(\w+)', ExportHandler),
], debug=True)
