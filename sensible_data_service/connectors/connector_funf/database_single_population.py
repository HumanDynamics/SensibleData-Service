from utils import database
import os
import fnmatch
import random
import time
from models import *
from utils import fail
from utils import log
import sqlite3
import shutil
import bson.json_util as json
import time
import hashlib
from anonymizer.anonymizer import Anonymizer
from collections import defaultdict
import sys, traceback
import authorization_manager.authorization_manager as authorization_manager
from django.conf import settings

import traceback
import pdb

def load_file(filename):
	#pdb.set_trace()
	log.log('Debug', 'Trying to populate db with ' + filename);
	mConnector = ConnectorFunf.objects.all()[0]
	db = database.Database()
	anonymizerObject = Anonymizer()
	
	documents_to_insert = defaultdict(list)
	
	proc_dir = os.path.join(mConnector.decrypted_path, 'processing')
	if not os.path.exists(proc_dir):
		os.makedirs(proc_dir)
		
	decrypted_filepath = os.path.join(mConnector.decrypted_path, filename)
	processing_filepath = os.path.join(proc_dir,filename)
	current_filepath = decrypted_filepath
	if os.path.exists(decrypted_filepath) and not os.path.exists(processing_filepath):
		try:
			# move to processing
			shutil.move(decrypted_filepath, proc_dir)
			current_filepath = processing_filepath
			# open connection to db file
			conn = sqlite3.connect(processing_filepath)
			cursor = conn.cursor()
			
			# get the meta data from db file
			meta = {}
			(meta['device'], meta['uuid'], meta['device_id'], meta['sensible_token'], meta['device_bt_mac']) = \
				cursor.execute('select device, uuid, device_id, sensible_token, device_bt_mac from file_info').fetchone()
			meta['device_id'] = anonymizerObject.anonymizeValue('device_id',meta['device_id'])
			
			#pdb.set_trace()
			# get the user associated with the token
			#meta['user'] = authorization_manager.getAuthorizationForToken(\
			#	'connector_funf.submit_data', meta['token']).user
			meta['user'] = 'TODO'
			for row in cursor.execute('select * from data'):
				doc = row_to_doc(row, meta['user'], anonymizerObject )
				if doc == None:
					continue
				documents_to_insert[doc['probe']].append(dict(doc.items() + meta.items()))
			
			cursor.close();
			#pdb.set_trace()
			for probe in documents_to_insert:
				db.insert(documents_to_insert[probe], probe)
				
			os.remove(current_filepath);
			
		except Exception as e:
			log.log('Error', str(e));
			if not 'already exists' in str(e):
				top = traceback.extract_stack()[-1]
				fail.fail(current_filepath, load_failed_path, 'Exception with file: ' + filename\
				+ '\n' + ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])]))
			else:
				pass
			
			return False

def row_to_doc(row, user, anonymizerObject):
	random.seed(time.time())
	#TODO: separate this sanitization
	data_raw = row[3].replace('android.bluetooth.device.extra.DEVICE','android_bluetooth_device_extra_DEVICE')\
		.replace('android.bluetooth.device.extra.NAME', 'android_bluetooth_device_extra_NAME')\
		.replace('android.bluetooth.device.extra.CLASS', 'android_bluetooth_device_extra_CLASS')\
		.replace('android.bluetooth.device.extra.RSSI', 'android_bluetooth_device_extra_RSSI')
	
	data = json.loads(data_raw)
	if data.has_key('PROBE'): #only get data from probes
		doc = {}
		doc['timestamp'] = float(row[2])
		doc['_id'] = hashlib.sha1(json.dumps(data)).hexdigest()+'_'+user+'_'+str(int(doc['timestamp']))+'_'+str(random.random())+'_'+str(random.random())
		doc['probe'] = data['PROBE'].replace('.','_')
		doc['data'] = anonymizerObject.anonymizeDocument(data, doc['probe'])
		doc['name'] = row[1]
		doc['timestamp_added'] = time.time()
		return doc
	else:
		return None
			
			