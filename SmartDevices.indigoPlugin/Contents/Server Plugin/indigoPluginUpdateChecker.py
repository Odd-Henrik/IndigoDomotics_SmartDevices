#!/usr/bin/env python2.5
# Filename: indigoPluginUpdateChecker.py
#
# Originally written by berkinet
# Conversion to module and email features by Travis Cook
#
# About:
#	This method checks for a specially-formatted file on a web server to determine if
#	there's been a new release of the plugin.  If there has, an entry will be made in
#	the log, and the user will optionally be emailed about the release.  The email
#	subject and body are set in the file on the server.
#
#
# Usage:
#
# 	At the top of your plugin.py:
#		import indigoPluginUpdateChecker
#
#	In your plugin's __Init__ method:
#		self.updater = indigoPluginUpdateChecker.updateChecker(self, versionFileUrl [,daysBetweenChecks])
#
#		where:
#			- serverUrl is the location of your update info file (see below).
#			The url must be formatted like "http://www.domain.com/folder/updateFile.html"
#			- daysBetweenChecks is optional and defaults to 1.  This controls how often the module
#		  	will check for updates automatically.  They can always be checked for manually by running
#		  	self.updater.checkVersionNow()
#
#
#	Then put the following in your startup method to see if a check is required at startup:
#		self.updater.checkVersionPoll()
#
#	And also in your runConcurrentThread so the module can see if it's time to check for an update:
#
#		 def runConcurrentThread(self):
#		 	# While Indigo hasn't told us to shutdown
#		 	while self.shutdown is False:
#		 		self.updater.checkVersionPoll()
#		 		self.sleep(1)
#		 def stopConcurrentThread(self):
#		 	self.shutdown = True
#
#
#	PluginConfig.xml:
#
#		The following field should exist in the plugin's config if you want to use the email feature.
#		If the field is blank then emails will of course be disabled.
#
#			<Field id="updaterEmail" type="textfield">
#				<Label>Email:</Label>
#			</Field>
#
#		Optionally a checkbox can also be used.
#
#			<Field id="updaterEmailsEnabled" type="checkbox" defaultValue="true">
#				<Label>Email Update Notifications:</Label>
#			</Field>
#
#		Some values are saved in the plugin's prefs for use by the updater:
#			'updaterLastCheck' = Last time an update check was performed (epoch time)
#			'updaterLastVersionEmailed' = The last version emailed to the user
#
#
#
#	Server File:
#
#		Sample VersionInfo.html file:
#
			# Version: 1.3.1
			# EmailSubject: DSC Alarm Indigo Plugin Update
			# EmailBody: The DSC Alarm Plugin you are using with Indigo has been updated.

			# The changes are:
			# - Change 1
			# - Change 2

			# The update can be downloaded at the link below.
			# http://www.frightideas.com/hobbies/dscAlarm/DSC_Alarm_Plugin.zip

			# This email was sent to you by Indigo at the request of the plugin.  You will
			# only be emailed once per release.  To disable these emails see the plugin's config.


import indigo
import re
import socket
import time
from urllib2 import urlopen


# noinspection PyBroadException
class updateChecker(object):

	def __init__(self, plugin, fileUrl, daysBetweenChecks=1):
		self.plugin = plugin
		self.fileUrl = fileUrl
		self.secondsBetweenAutoChecks = daysBetweenChecks * 86400
		self.nextCheck = int(self.plugin.pluginPrefs.get('updaterLastCheck', '0')) + self.secondsBetweenAutoChecks


	def errorLog(self, log):
		indigo.server.log(log, isError=True)


	def checkVersionPoll(self):
		# Did we check if there was an update within the last
		timeNow = time.time()
		# If the version wasn't checked within our time period then check
		if timeNow > self.nextCheck:
			self.checkVersionNow()


	def checkVersionNow(self):

		self.plugin.debugLog(u"versionCheck: Started")

		# Save the last check time (now) in the plugin's config and our global variable
		timeNow = time.time()
		self.plugin.pluginPrefs[u'updaterLastCheck'] = timeNow
		self.nextCheck = timeNow + self.secondsBetweenAutoChecks

		# Get plugin version
		myVersion = str(self.plugin.pluginVersion)
		self.plugin.debugLog('versionCheck: Version Server Url:%s' % self.fileUrl)
		socket.setdefaulttimeout(3)

		# Try to grab the version file
		try:
			f = urlopen(self.fileUrl)
		except:
			self.errorLog(u"versionCheck: Unable to reach the version server.")
			return

		# Parse the file
		try:
			lines = f.read().split('\n')
			if lines[0].startswith('Version:'):
				latestVersion = lines[0][8:].strip()
			else:
				self.plugin.debugLog(u'versionCheck: The version file does not start with "Version:"')
				self.errorLog(u"versionCheck: There was an error parsing the server's version file.")
				return
		except:
			self.errorLog(u"versionCheck: Error parsing the server's version file.")
			return


		# Compare the version in the server file to ours
		if myVersion < latestVersion:
			self.errorLog(u"You are running v%s. A newer version, v%s is available." % (myVersion, latestVersion))
		else:
			indigo.server.log(u'Your plugin version, v%s, is current.' % myVersion)
			# This version is current so we might as well exit
			return


		########################################################
		# Email code only from here down

		# Get Email Address
		emailAddress = self.plugin.pluginPrefs.get(u'updaterEmail', '')
		if len(emailAddress) == 0:
			self.plugin.debugLog(u"versionCheck: No email address for updates found in the config.")

		# If there's a checkbox in the config in addition to the email address text box
		# then let the checkbox decide if we should send emails or not
		if self.plugin.pluginPrefs.get(u'updaterEmailsEnabled', True) is False:
			emailAddress = ''

		# If we do not have an email address, or emailing is disabled, then exit
		if len(emailAddress) == 0:
			return

		# Get last version Emailed to the user
		lastVersionEmailed = self.plugin.pluginPrefs.get('updaterLastVersionEmailed', '0')

		# Did we already email the user about this version?
		if lastVersionEmailed == latestVersion:
			self.plugin.debugLog(u"versionCheck: We already emailed the user about this version, exiting.")
			return

		# Check if the version file contains any email information
		# If not maybe the developer doesn't want this feature.  Let's abort.
		if (len(lines) == 1) or ('Email' not in lines[1]):
			self.plugin.debugLog(u"versionCheck: No email data found in the file, exiting.")
			return

		# Parse the rest of the file for the email information
		try:
			if (lines[1].startswith('EmailSubject:')) and (lines[2].startswith('EmailBody:')):
				emailSubject = lines[1][13:].strip()
				emailBody = lines[2][10:].lstrip() + "\n"
				emailBody += "\n".join(lines[3:]) + "\n"

				#self.plugin.debugLog(u"Subject: *%s*" % emailSubject)
				#self.plugin.debugLog(u"Body: *%s*" % emailBody)

				indigo.server.log(u"Emailing the user about the new version.")

				# Save this version as the last one emailed in the prefs
				self.plugin.pluginPrefs[u'updaterLastVersionEmailed'] = latestVersion

				indigo.server.sendEmailTo(emailAddress, subject=emailSubject, body=emailBody)

			else:
				self.plugin.debugLog(u'versionCheck: The "EmailSubject:" and "EmailBody:" lines were not found.')
				self.errorLog(u"versionCheck: There was an error parsing email data from the server's version file.")
		except:
			self.errorLog(u"versionCheck: Error parsing the email portion of the server's version file.")
			return
