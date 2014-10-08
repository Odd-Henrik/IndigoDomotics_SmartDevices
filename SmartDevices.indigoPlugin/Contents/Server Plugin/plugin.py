#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2014, Odd-Henrik Aasen. All rights reserved.
# http://www.odd-henrik.com

# noinspection PyUnresolvedReferences
import indigo

import os
import sys
import random

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

################################################################################
kHvacModeEnumToStrMap = {
    indigo.kHvacMode.Cool				: u"cool",
    indigo.kHvacMode.Heat				: u"heat",
    indigo.kHvacMode.HeatCool			: u"auto",
    indigo.kHvacMode.Off				: u"off",
    indigo.kHvacMode.ProgramHeat		: u"program heat",
    indigo.kHvacMode.ProgramCool		: u"program cool",
    indigo.kHvacMode.ProgramHeatCool	: u"program auto"
}

kFanModeEnumToStrMap = {
    indigo.kFanMode.AlwaysOn			: u"always on",
    indigo.kFanMode.Auto				: u"auto"
}


def _lookupActionStrFromHvacMode(hvacMode):
    return kHvacModeEnumToStrMap.get(hvacMode, u"unknown")


def _lookupActionStrFromFanMode(fanMode):
    return kFanModeEnumToStrMap.get(fanMode, u"unknown")

################################################################################
# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyPep8
class Plugin(indigo.PluginBase):
    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        #del valuesDict["enableDebug"]
        if pluginPrefs.get("enableDebug", ""):
            self.debug = True
            indigo.server.log("debug enabled")
        else:
            self.debug = False
            indigo.server.log("debug disabled")

        self.debugLog("debug: " + str(self.debug))

    def __del__(self):
        indigo.PluginBase.__del__(self)

    ########################################
    # Internal utility methods. Some of these are useful to provide
    # a higher-level abstraction for accessing/changing thermostat
    # properties or states.
    ######################
    def _getTempSensorCount(self, dev):
        return int(dev.pluginProps["NumTemperatureInputs"])

    def _getHumiditySensorCount(self, dev):
        return int(dev.pluginProps["NumHumidityInputs"])

    ######################
    def _changeTempSensorCount(self, dev, count):
        newProps = dev.pluginProps
        newProps["NumTemperatureInputs"] = count
        dev.replacePluginPropsOnServer(newProps)

    def _changeHumiditySensorCount(self, dev, count):
        newProps = dev.pluginProps
        newProps["NumHumidityInputs"] = count
        dev.replacePluginPropsOnServer(newProps)

    def _changeAllTempSensorCounts(self, count):
        for dev in indigo.devices.iter("self"):
            self._changeTempSensorCount(dev, count)

    def _changeAllHumiditySensorCounts(self, count):
        for dev in indigo.devices.iter("self"):
            self._changeHumiditySensorCount(dev, count)

    ######################
    def _changeTempSensorValue(self, dev, index, value):
        # Update the temperature value at index. If index is greater than the "NumTemperatureInputs"
        # an error will be displayed in the Event Log "temperature index out-of-range"
        stateKey = u"temperatureInput" + str(index)
        dev.updateStateOnServer(stateKey, value, uiValue="%d °F" % value)
        self.debugLog(u"\"%s\" called update %s %d" % (dev.name, stateKey, value))

    def _changeHumiditySensorValue(self, dev, index, value):
        # Update the humidity value at index. If index is greater than the "NumHumidityInputs"
        # an error will be displayed in the Event Log "humidity index out-of-range"
        stateKey = u"humidityInput" + str(index)
        dev.updateStateOnServer(stateKey, value, uiValue="%d °F" % value)
        self.debugLog(u"\"%s\" called update %s %d" % (dev.name, stateKey, value))

    ######################
    # Poll all of the states from the thermostat and pass new values to
    # Indigo Server.
    def _refreshStatesFromHardware(self, dev, logRefresh, commJustStarted):
        pass
        # As an example here we update the temperature and humidity
        # sensor states to random values.
        #	Other states that should also be updated:
        # ** IMPLEMENT ME **
        # dev.updateStateOnServer("setpointHeat", floating number here)
        # dev.updateStateOnServer("setpointCool", floating number here)
        # dev.updateStateOnServer("hvacOperationMode", some indigo.kHvacMode.* value here)
        # dev.updateStateOnServer("hvacFanMode", some indigo.kFanMode.* value here)
        # dev.updateStateOnServer("hvacCoolerIsOn", True or False here)
        # dev.updateStateOnServer("hvacHeaterIsOn", True or False here)
        # dev.updateStateOnServer("hvacFanIsOn", True or False here)

        #if commJustStarted:
            # As an example, we force these thermostat states to specific values.
        #     if "setpointHeat" in dev.states:
        #         dev.updateStateOnServer("setpointHeat", 66.5, uiValue="66.5 °F")
        #     if "setpointCool" in dev.states:
        #         dev.updateStateOnServer("setpointCool", 77.5, uiValue="77.5 °F")
        #     if "hvacOperationMode" in dev.states:
        #         dev.updateStateOnServer("hvacOperationMode", indigo.kHvacMode.HeatCool)
        #     if "hvacFanMode" in dev.states:
        #         dev.updateStateOnServer("hvacFanMode", indigo.kFanMode.Auto)
        #     dev.updateStateOnServer("backlightBrightness", 85, uiValue="85%")
        # if logRefresh:
        #     if "setpointHeat" in dev.states:
        #         indigo.server.log(u"received \"%s\" cool setpoint update to %.1f°" % (dev.name, dev.states["setpointHeat"]))
        #     if "setpointCool" in dev.states:
        #         indigo.server.log(u"received \"%s\" heat setpoint update to %.1f°" % (dev.name, dev.states["setpointCool"]))
        #     if "hvacOperationMode" in dev.states:
        #         indigo.server.log(u"received \"%s\" main mode update to %s" % (dev.name, _lookupActionStrFromHvacMode(dev.states["hvacOperationMode"])))
        #     if "hvacFanMode" in dev.states:
        #         indigo.server.log(u"received \"%s\" fan mode update to %s" % (dev.name, _lookupActionStrFromFanMode(dev.states["hvacFanMode"])))
        #     indigo.server.log(u"received \"%s\" backlight brightness update to %d%%" % (dev.name, dev.states["backlightBrightness"]))

    ######################
    # Process action request from Indigo Server to change main thermostat's main mode.
    def _handleChangeHvacModeAction(self, dev, newHvacMode):
        # Command hardware module (dev) to change the thermostat mode here:
        # ** IMPLEMENT ME **
        sendSuccess = True		# Set to False if it failed.

        actionStr = _lookupActionStrFromHvacMode(newHvacMode)
        if sendSuccess:
            # If success then log that the command was successfully sent.
            indigo.server.log(u"sent \"%s\" mode change to %s" % (dev.name, actionStr))

            # And then tell the Indigo Server to update the state.
            if "hvacOperationMode" in dev.states:
                dev.updateStateOnServer("hvacOperationMode", newHvacMode)
                self._runHVACLogic(indigo.devices[dev.id])
        else:
            # Else log failure but do NOT update state on Indigo Server.
            indigo.server.log(u"send \"%s\" mode change to %s failed" % (dev.name, actionStr), isError=True)

    ######################
    # Process action request from Indigo Server to change thermostat's fan mode.
    def _handleChangeFanModeAction(self, dev, newFanMode):
        # Command hardware module (dev) to change the fan mode here:
        # ** IMPLEMENT ME **
        sendSuccess = True		# Set to False if it failed.

        actionStr = _lookupActionStrFromFanMode(newFanMode)
        if sendSuccess:
            # If success then log that the command was successfully sent.
            indigo.server.log(u"sent \"%s\" fan mode change to %s" % (dev.name, actionStr))

            # And then tell the Indigo Server to update the state.
            if "hvacFanMode" in dev.states:
                dev.updateStateOnServer("hvacFanMode", newFanMode)
        else:
            # Else log failure but do NOT update state on Indigo Server.
            indigo.server.log(u"send \"%s\" fan mode change to %s failed" % (dev.name, actionStr), isError=True)

    ######################
    # Process action request from Indigo Server to change a cool/heat setpoint.
    def _handleChangeSetpointAction(self, dev, newSetpoint, logActionName, stateKey):
        if newSetpoint < 0.0:
            newSetpoint = 0.0		# Arbitrary -- set to whatever hardware minimum setpoint value is.
        elif newSetpoint > 50.0:
            newSetpoint = 50.0		# Arbitrary -- set to whatever hardware maximum setpoint value is.

        sendSuccess = False

        if stateKey == u"setpointCool":
            # Command hardware module (dev) to change the cool setpoint to newSetpoint here:
            # ** IMPLEMENT ME **
            sendSuccess = True			# Set to False if it failed.
        elif stateKey == u"setpointHeat":
            # Command hardware module (dev) to change the heat setpoint to newSetpoint here:
            # ** IMPLEMENT ME **
            sendSuccess = True			# Set to False if it failed.

        if sendSuccess:
            # If success then log that the command was successfully sent.
            indigo.server.log(u"sent \"%s\" %s to %.1f°" % (dev.name, logActionName, newSetpoint))

            # And then tell the Indigo Server to update the state.
            if stateKey in dev.states:
                dev.updateStateOnServer(stateKey, newSetpoint, uiValue="%.1f °F" % newSetpoint)
        else:
            # Else log failure but do NOT update state on Indigo Server.
            indigo.server.log(u"send \"%s\" %s to %.1f° failed" % (dev.name, logActionName, newSetpoint), isError=True)

    ########################################
    def startup(self):
        self.debugLog(u"startup called")
        self.debugLog(u"Subscribing To Changes")
        indigo.devices.subscribeToChanges()

    def shutdown(self):
        self.debugLog(u"shutdown called")

    ########################################

    def closedPrefsConfigUi (self, valuesDict, UserCancelled):
        if UserCancelled is False:
            logLevel = valuesDict["enableDebug"]

            if logLevel:
                self.debug = True
                indigo.server.log("debug enabled")
            else:
                self.debug = False
                indigo.server.log("debug disabled")

            if self.debug: indigo.server.log ("Smart Devices plugin preferences have been updated.")


    def runConcurrentThread(self):
        try:
            while True:
                for dev in indigo.devices.iter("self"):
                    if not dev.enabled or not dev.configured:
                        continue

                    # Plugins that need to poll out the status from the thermostat
                    # could do so here, then broadcast back the new values to the
                    # Indigo Server.

                    #self._refreshStatesFromHardware(dev, False, False)

                self.sleep(200)
        except self.StopThread:
            pass	# Optionally catch the StopThread exception and do any needed cleanup.

    ########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        return True, valuesDict

    ########################################
    def deviceStartComm(self, dev):
        # Called when communication with the hardware should be established.
        # Here would be a good place to poll out the current states from the
        # thermostat. If periodic polling of the thermostat is needed (that
        # is, it doesn't broadcast changes back to the plugin somehow), then
        # consider adding that to runConcurrentThread() above.

        #self._refreshStatesFromHardware(dev, True, True)
        self.debugLog(u"-- deviceStartComm --")

        newProps = dev.pluginProps

        self.debugLog(u"Number of temperature sensors: " + str(len(self._getTemperatureSensorsIdsInVirtualDevice(dev))))
        #self._changeTempSensorCount(dev, len(self._getTemperatureSensorsIdsInVirtualDevice(dev)))
        newProps["NumTemperatureInputs"] = len(self._getTemperatureSensorsIdsInVirtualDevice(dev))

        self.debugLog(u"Number of humidity sensors: " + str(len(self._getHumiditySensorsIdsInVirtualDevice(dev))))
        #self._changeHumiditySensorCount(dev, len(self._getHumiditySensorsIdsInVirtualDevice(dev)))
        newProps["NumHumidityInputs"] = len(self._getHumiditySensorsIdsInVirtualDevice(dev))

        self.debugLog("Number of primary Heater Devices: " + str(len(newProps.get("primaryHeaterDevice", ""))))

        # Check to see if we are using any devices that supports HVAC opMode and Need Epuipment status
        if len(newProps.get("primaryHeaterDevice", "")) > 0 or len(newProps.get("secondaryHeaterDevice", "")) > 0 or len(newProps.get("acHeatPumpDevice", "")) > 0 or len(newProps.get("ventilationDevice", "")):
            newProps["SupportsHvacOperationMode"] = True
            newProps["ShowCoolHeatEquipmentStateUI"] = True
        else:
            newProps["SupportsHvacOperationMode"] = False
            newProps["ShowCoolHeatEquipmentStateUI"] = False

        # Check to se if we support Heat Set Point
        if len(newProps.get("primaryHeaterDevice", "")) > 0 or len(newProps.get("secondaryHeaterDevice", "")) > 0 or len(newProps.get("heaterDevice", "")) > 0:
            newProps["SupportsHeatSetpoint"] = True
        else:
            newProps["SupportsHeatSetpoint"] = False

        # Check to se if we support Cool Set Point and Fan mode
        if len(newProps.get("acHeatPumpDevice", "")) > 0 or len(newProps.get("ventilationDevice", "")) > 0:
            newProps["SupportsCoolSetpoint"] = True
            newProps["SupportsHvacFanMode"] = True
        else:
            newProps["SupportsCoolSetpoint"] = False
            newProps["SupportsHvacFanMode"] = False

        # Have not implemented anything useful for Status Request yet.
        newProps["supportsStatusRequest"] = False
        # This seems to have no effect, a bug?
        #self.debugLog("supportsStatusRequest: " + str(newProps["supportsStatusRequest"]))

        dev.replacePluginPropsOnServer(newProps)

        self._getAllSensorsValuesNow(dev)
        self._runHVACLogic(dev)
        pass


    def deviceStopComm(self, dev):
        # Called when communication with the hardware should be shutdown.
        pass

    def _getSensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()

        self.debugLog("test 6")
        if dev.pluginProps.get("primaryTemperatureSensors", ""):
            for sens in (dev.pluginProps["primaryTemperatureSensors"]):
                self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))

        if dev.pluginProps.get("floorTemperatureSensor", ""):
            sensorDevices.append(int(dev.pluginProps["floorTemperatureSensor"]))

        if dev.pluginProps.get("outsideTemperatureSensor", ""):
            sensorDevices.append(int(dev.pluginProps["outsideTemperatureSensor"]))

        if dev.pluginProps.get("outsideHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["outsideHumiditySensor"]))

        if dev.pluginProps.get("optionalHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["optionalHumiditySensor"]))

        if dev.pluginProps.get("ambientHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["ambientHumiditySensor"]))

        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices

    def _getHumiditySensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()

        if dev.pluginProps.get("outsideHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["outsideHumiditySensor"]))

        if dev.pluginProps.get("optionalHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["optionalHumiditySensor"]))

        if dev.pluginProps.get("ambientHumiditySensor", ""):
            sensorDevices.append(int(dev.pluginProps["ambientHumiditySensor"]))

        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices

    def _getTemperatureSensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()


        if dev.pluginProps.get("primaryTemperatureSensors", ""):
            for sens in (dev.pluginProps["primaryTemperatureSensors"]):
                self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))
            #sensorDevices.append(int(dev.pluginProps["temperatureSensor"]))

        if dev.pluginProps.get("floorTemperatureSensor", ""):
            sensorDevices.append(int(dev.pluginProps["floorTemperatureSensor"]))

        if dev.pluginProps.get("outsideTemperatureSensor", ""):
            sensorDevices.append(int(dev.pluginProps["outsideTemperatureSensor"]))



        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices



    def _handleChangeTemperatureSensors(self, thermostatDev, sensorDev):
        self.debugLog(u"************************** handleChangeTemperatureSensors *************************************")
        self.debugLog(u"*************************** " + str(sensorDev.name) + u" **************************************")
        self.debugLog(u"Sensor Device update found, sensor value = " + str(sensorDev.sensorValue))



        # Temperature sensors
        if thermostatDev.pluginProps.get("primaryTemperatureSensors", ""):
             for sens in (dev.pluginProps["primaryTemperatureSensors"]):
                if sensorDev.id == int(sens):
                    tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(sens)) + 1
                    thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%d °C" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("floorTemperatureSensor", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["floorTemperatureSensor"]):
                tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["floorTemperatureSensor"])) + 1
                thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%d °C" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("outsideTemperatureSensor", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["outsideTemperatureSensor"]):
                tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["outsideTemperatureSensor"])) + 1
                thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%d °C" % sensorDev.sensorValue)

        # Humidity sensors
        if thermostatDev.pluginProps.get("outsideHumiditySensor", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["outsideHumiditySensor"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["outsideHumiditySensor"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="%d" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("optionalHumiditySensor", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["optionalHumiditySensor"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["optionalHumiditySensor"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="%d" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("ambientHumiditySensor", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["ambientHumiditySensor"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["ambientHumiditySensor"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="%d" % sensorDev.sensorValue)


    def deviceUpdated(self, origDev, newDev):
        indigo.PluginBase.deviceUpdated(self, origDev, newDev)

        for dev in indigo.devices.iter("self"):
            if not dev.enabled or not dev.configured:
                continue

            self.debugLog("DeviceUpdate for device:" + dev.name + " Of Type: " + dev.deviceTypeId)
            if newDev.id in  self._getSensorsIdsInVirtualDevice(dev):
                self._handleChangeTemperatureSensors(dev, newDev)
                self._runHVACLogic(dev)

    def _getAllSensorsValuesNow(self, dev):
        for sensorId in self._getSensorsIdsInVirtualDevice(dev):
            self._handleChangeTemperatureSensors(dev, indigo.devices[sensorId])


    def _runHVACLogic(self, virDev):
        # Getting all the devices
        self.debugLog("=============== Running HVAC Logic ================")
        self.debugLog("Getting all the devices")
        self.debugLog("Temperature Sensors:")
        # Temperature sensors
        primaryTemperatureSensors = False
        floorTemperatureSensor = False
        outsideTemperatureSensor = False
        temperatureSensor = False

        if virDev.pluginProps.get("primaryTemperatureSensors", ""):
            primaryTemperatureSensors = indigo.devices[int(virDev.pluginProps["primaryTemperatureSensors"])]
            self.debugLog(primaryTemperatureSensors.name)

        if virDev.pluginProps.get("floorTemperatureSensor", ""):
            floorTemperatureSensor = indigo.devices[int(virDev.pluginProps["floorTemperatureSensor"])]
            self.debugLog(floorTemperatureSensor.name)

        if virDev.pluginProps.get("outsideTemperatureSensor", ""):
            outsideTemperatureSensor = indigo.devices[int(virDev.pluginProps["outsideTemperatureSensor"])]
            self.debugLog(outsideTemperatureSensor.name)

        # Humidity sensors
        outsideHumiditySensor = False
        optionalHumiditySensor = False
        ambientHumiditySensor = False

        self.debugLog("Humidity Sensors:")
        if virDev.pluginProps.get("outsideHumiditySensor", ""):
            outsideHumiditySensor = indigo.devices[int(virDev.pluginProps["outsideHumiditySensor"])]
            self.debugLog(outsideHumiditySensor.name)

        if virDev.pluginProps.get("optionalHumiditySensor", ""):
            optionalHumiditySensor = indigo.devices[int(virDev.pluginProps["optionalHumiditySensor"])]
            self.debugLog(optionalHumiditySensor.name)

        if virDev.pluginProps.get("ambientHumiditySensor", ""):
            ambientHumiditySensor = indigo.devices[int(virDev.pluginProps["ambientHumiditySensor"])]
            self.debugLog(ambientHumiditySensor.name)

        # HVAC Devices
        acHeatPumpDevice = False
        primaryHeaterDevice = False
        secondaryHeaterDevice = False
        ventilationDevice = False

        self.debugLog("HVAC Devices:")
        if virDev.pluginProps.get("acHeatPumpDevice", ""):
            acHeatPumpDevice = indigo.devices[int(virDev.pluginProps["acHeatPumpDevice"])]
            self.debugLog(acHeatPumpDevice.name)

        if virDev.pluginProps.get("primaryHeaterDevice", ""):
            primaryHeaterDevice = indigo.devices[int(virDev.pluginProps["primaryHeaterDevice"])]
            self.debugLog(primaryHeaterDevice.name)

        if virDev.pluginProps.get("secondaryHeaterDevice", ""):
            secondaryHeaterDevice = indigo.devices[int(virDev.pluginProps["secondaryHeaterDevice"])]
            self.debugLog(ambientHumiditySensor.name)

        if virDev.pluginProps.get("ventilationDevice", ""):
            ventilationDevice = indigo.devices[int(virDev.pluginProps["ventilationDevice"])]
            self.debugLog(ventilationDevice.name)

        # Settings
        configTemperatureDelta = False
        self.debugLog("Settings:")
        if virDev.pluginProps.get("configTemperatureDelta", ""):
            configTemperatureDelta = float(virDev.pluginProps["configTemperatureDelta"])
            self.debugLog("configTemperatureDelta: " + str(configTemperatureDelta))

        self.debugLog("Cool Set Point: " + str(virDev.coolSetpoint))
        self.debugLog("Heat Set Point: " + str(virDev.heatSetpoint))
    #		self.debugLog("hvacOperationMode: " + str(_lookupActionStrFromHvacMode(virDev.states["hvacOperationMode"])))
    #		self.debugLog("hvacOperationMode: " + str(virDev.states["hvacOperationMode"]))
        self.debugLog("hvacOperationMode: " + str(virDev.hvacMode))
        self.debugLog("fanMode: " + str(virDev.fanMode))
        self.debugLog("=============== Done Getting Devices ================")

        if virDev.hvacMode == indigo.kHvacMode.Off:
            self._turnOffAllHVACDevices(virDev)
        elif virDev.hvacMode == indigo.kHvacMode.Cool:
            pass
        elif virDev.hvacMode == indigo.kHvacMode.Heat:
            self._heat(virDev, primaryHeaterDevice, primaryTemperatureSensors, secondaryHeaterDevice,
                       floorTemperatureSensor, outsideTemperatureSensor)
            #self._heat(virDev, primaryHeaterDevice, temperatureSensor, None, None, None)
        elif virDev.hvacMode == indigo.kHvacMode.HeatCool:
            pass

        return True



            #indigo.kHvacMode.Cool				: u"cool",
            #indigo.kHvacMode.Heat				: u"heat",
            #indigo.kHvacMode.HeatCool			: u"auto",
            #indigo.kHvacMode.Off				: u"off",
            #indigo.kHvacMode.ProgramHeat		: u"program heat",
            #indigo.kHvacMode.ProgramCool		: u"program cool",
            #indigo.kHvacMode.ProgramHeatCool

    def _heat(self, virDev, primaryHeaterDevice, primaryTemperatureSensors, secondaryHeaterDevice,
              floorTemperatureSensor, outsideTemperatureSensor):
        # Heater logic
        heater = primaryHeaterDevice
        sensorTemp = primaryTemperatureSensors.sensorValue
        setTemp = virDev.heatSetpoint
        deltaTemp = float(virDev.pluginProps["configTemperatureDelta"])

        self.debugLog("********* Heat Logic Run for: " + virDev.name)
        self.debugLog("Heater: " + heater.name)
        self.debugLog("sensorTemp: " + str(sensorTemp))
        self.debugLog("Set Temp: " + str(setTemp))
        self.debugLog("Delta Temp: " + str(deltaTemp))

        if (sensorTemp < (setTemp - deltaTemp)) and not heater.onState:
            indigo.device.turnOn(heater)
            self.debugLog("Heater On")
            virDev.updateStateOnServer("hvacHeaterIsOn", True)
        elif (sensorTemp > (setTemp + deltaTemp)) and heater.onState:
            indigo.device.turnOff(heater)
            self.debugLog("Heater Off")
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        else:
            #indigo.device.turnOff(heater)
            self.debugLog("In delta or set")
            if heater.onState:
                virDev.updateStateOnServer("hvacHeaterIsOn", True)
            else:
                virDev.updateStateOnServer("hvacHeaterIsOn", False)

        if sensorTemp > (setTemp + deltaTemp + 1):
            self.debugLog("Too warm, turning off heater")
            indigo.device.turnOff(heater)
            self.debugLog("Heater Off")
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        elif sensorTemp < (setTemp - deltaTemp - 1):
            self.debugLog("Too cold, turning on heater")
            indigo.device.turnOn(heater)
            self.debugLog("Heater On")
            virDev.updateStateOnServer("hvacHeaterIsOn", True)



    def _turnOffAllHVACDevices(self, virDev):
        if virDev.pluginProps.get("acHeatPumpDevice", ""):
            acHeatPumpDevice = indigo.devices[int(virDev.pluginProps["acHeatPumpDevice"])]
            indigo.device.turnOff(acHeatPumpDevice)

        if virDev.pluginProps.get("primaryHeaterDevice", ""):
            primaryHeaterDevice = indigo.devices[int(virDev.pluginProps["primaryHeaterDevice"])]
            indigo.device.turnOff(primaryHeaterDevice)

        if virDev.pluginProps.get("secondaryHeaterDevice", ""):
            secondaryHeaterDevice = indigo.devices[int(virDev.pluginProps["secondaryHeaterDevice"])]
            indigo.device.turnOff(secondaryHeaterDevice)

        if virDev.pluginProps.get("ventilationDevice", ""):
            ventilationDevice = indigo.devices[int(virDev.pluginProps["ventilationDevice"])]
            indigo.device.turnOff(ventilationDevice)

        if virDev.pluginProps.get("ventilationDevice", ""):
            ventilationDevice = indigo.devices[int(virDev.pluginProps["ventilationDevice"])]
            indigo.device.turnOff(ventilationDevice)




    ########################################
    # Thermostat Action callback
    ######################
    # Main thermostat action bottleneck called by Indigo Server.
    def actionControlThermostat(self, action, dev):
        ###### SET HVAC MODE ######
        if action.thermostatAction == indigo.kThermostatAction.SetHvacMode:
            self._handleChangeHvacModeAction(dev, action.actionMode)

        ###### SET FAN MODE ######
        elif action.thermostatAction == indigo.kThermostatAction.SetFanMode:
            self._handleChangeFanModeAction(dev, action.actionMode)

        ###### SET COOL SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.SetCoolSetpoint:
            newSetpoint = action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"change cool setpoint", u"setpointCool")

        ###### SET HEAT SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.SetHeatSetpoint:
            newSetpoint = action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"change heat setpoint", u"setpointHeat")

        ###### DECREASE/INCREASE COOL SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.DecreaseCoolSetpoint:
            newSetpoint = dev.coolSetpoint - 0.5 #action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"decrease cool setpoint", u"setpointCool")

        elif action.thermostatAction == indigo.kThermostatAction.IncreaseCoolSetpoint:
            newSetpoint = dev.coolSetpoint + 0.5 #action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"increase cool setpoint", u"setpointCool")

        ###### DECREASE/INCREASE HEAT SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.DecreaseHeatSetpoint:
            newSetpoint = dev.heatSetpoint - 0.5 #action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"decrease heat setpoint", u"setpointHeat")

        elif action.thermostatAction == indigo.kThermostatAction.IncreaseHeatSetpoint:
            newSetpoint = dev.heatSetpoint + 0.5 #action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"increase heat setpoint", u"setpointHeat")

        ###### REQUEST STATE UPDATES ######
        elif action.thermostatAction in [indigo.kThermostatAction.RequestStatusAll, indigo.kThermostatAction.RequestMode,
        indigo.kThermostatAction.RequestEquipmentState, indigo.kThermostatAction.RequestTemperatures, indigo.kThermostatAction.RequestHumidities,
        indigo.kThermostatAction.RequestDeadbands, indigo.kThermostatAction.RequestSetpoints]:
            self._refreshStatesFromHardware(dev, True, False)

    ########################################
    # General Action callback
    ######################
    def actionControlGeneral(self, action, dev):
        ###### BEEP ######
        if action.deviceAction == indigo.kDeviceGeneralAction.Beep:
            # Beep the hardware module (dev) here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "beep request"))

        ###### ENERGY UPDATE ######
        elif action.deviceAction == indigo.kDeviceGeneralAction.EnergyUpdate:
            # Request hardware module (dev) for its most recent meter data here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "energy update request"))

        ###### ENERGY RESET ######
        elif action.deviceAction == indigo.kDeviceGeneralAction.EnergyReset:
            # Request that the hardware module (dev) reset its accumulative energy usage data here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "energy reset request"))

        ###### STATUS REQUEST ######
        elif action.deviceAction == indigo.kDeviceGeneralAction.RequestStatus:
            # Query hardware module (dev) for its current status here. This differs from the
            # indigo.kThermostatAction.RequestStatusAll action - for instance, if your thermo
            # is battery powered you might only want to update it only when the user uses
            # this status request (and not from the RequestStatusAll). This action would
            # get all possible information from the thermostat and the other call
            # would only get thermostat-specific information:
            # ** GET BATTERY INFO **
            # and call the common function to update the thermo-specific data
            self._refreshStatesFromHardware(dev, True, False)
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "status request"))

    ########################################
    # Custom Plugin Action callbacks (defined in Actions.xml)
    ######################

    #setEnableDebugUi
    #getActionConfigUiValues
    # def getMenuActionConfigUiValues(self, menuId):
    #     indigo.server.log("getActionConfigUI")
    #     valuesDict = indigo.Dict()
    #     errorMsgDict = indigo.Dict()
    #     if menuId == "menuConfigure":
    #         if self.pluginPrefs["enableDebug"]:
    #             valuesDict["enableDebug"] = self.pluginPrefs["enableDebug"]
    #
    #         else:
    #             valuesDict["enableDebug"] = False
    #
    #     return valuesDict, errorMsgDict
    #
    # def changeDebugMode(self, valuesDict, TypeID):
    #     indigo.server.log("debug change to: " + str(valuesDict["enableDebug"]))
    #
    #     indigo.server.log("enableDebug UI: " + str(valuesDict["enableDebug"]))
    #     if valuesDict["enableDebug"]:
    #         self.debug = True
    #         indigo.server.log("debug true")
    #         self.pluginPrefs["enableDebug"] = True
    #     else:
    #         self.debug = False
    #         indigo.server.log("debug false")
    #         self.pluginPrefs["enableDebug"] = False
    #
    #     return True



    #################################################
    # Config button callback methods
    #################################################

    def ClearHVACDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["primaryHeaterDevice"] = ""
        valuesDict["secondaryHeaterDevice"] = ""
        valuesDict["ventilationDevice"] = ""
        valuesDict["acHeatPumpDevice"] = ""
        return valuesDict


    def ClearTemperatureDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["primaryTemperatureSensors"] = ""
        valuesDict["floorTemperatureSensor"] = ""
        valuesDict["outsideTemperatureSensor"] = ""
        return valuesDict

    def ClearHumidityDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["ambientHumiditySensor"] = ""
        valuesDict["optionalHumiditySensor"] = ""
        valuesDict["outsideHumiditySensor"] = ""
        return valuesDict

