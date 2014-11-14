#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2014, Odd-Henrik Aasen. All rights reserved.
# http://www.odd-henrik.com
##############

# noinspection PyUnresolvedReferences
import indigo

import os
import sys
import random
import datetime

import indigoPluginUpdateChecker


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


# noinspection PyPep8Naming
def _lookupActionStrFromHvacMode(hvacMode):
    return kHvacModeEnumToStrMap.get(hvacMode, u"unknown")

def _lookupHvacModeFromActionStr(actionStr):
    for mode in kHvacModeEnumToStrMap:
        if kHvacModeEnumToStrMap.get(mode) == actionStr:
            indigo.server.log(u"Val Key: " + str(mode))
            return mode
    return False

def _lookupActionStrFromFanMode(fanMode):
    return kFanModeEnumToStrMap.get(fanMode, u"unknown")

################################################################################
# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyPep8,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyPep8Naming,PyBroadException
class Plugin(indigo.PluginBase):
    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        #Updatecheker
        self.updater = indigoPluginUpdateChecker.updateChecker(self, "http://odd-henrik.com/smartdevices/versionInfoFile.html", 1)

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
        dev.updateStateOnServer(stateKey, value, uiValue="%.1f°" % value)
        self.debugLog(u"\"%s\" called update %s %.1f°" % (dev.name, stateKey, value))

    def _changeHumiditySensorValue(self, dev, index, value):
        # Update the humidity value at index. If index is greater than the "NumHumidityInputs"
        # an error will be displayed in the Event Log "humidity index out-of-range"
        stateKey = u"humidityInput" + str(index)
        dev.updateStateOnServer(stateKey, value, uiValue="%.1f°" % value)
        self.debugLog(u"\"%s\" called update %s %.1f°" % (dev.name, stateKey, value))

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
        #Setting defaults for min and max setpoint value (C)
        maxSetpointValue = 50
        minSetpointValue = 0

        #Getting configuration for min and max setpoint values
        if self.pluginPrefs.get("maxSetpointValue", ""):
            try:
                maxSetpointValue = float(self.pluginPrefs.get("maxSetpointValue", ""))
            except Exception, err:
                self.errorLog("ERROR in setting Maximum allowed Setpoint Value: %s. Using defaults: %s" % (str(err), str(maxSetpointValue)))

        if self.pluginPrefs.get("minSetpointValue", ""):
            try:
                minSetpointValue = float(self.pluginPrefs.get("minSetpointValue", ""))
            except Exception, err:
                self.errorLog("ERROR in setting Minimum allowed Setpoint Value: %s. Using defaults: %s" % (str(err), str(minSetpointValue)))

        #Testng to see if new setpoint value is in range.
        if newSetpoint < minSetpointValue:
            newSetpoint = minSetpointValue
        elif newSetpoint > maxSetpointValue:
            newSetpoint = maxSetpointValue

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
                dev.updateStateOnServer(stateKey, newSetpoint, uiValue="SetP: %.1f°" % newSetpoint)

                #Syncing with variable if configures so
                #if dev.pluginProps.get(u"useVariableSetPoint", "") and dev.pluginProps.get(u"SetPointVariable", ""):
                if self._validateAndGetSetPointVariable(dev):
                    setpointVariable = self._validateAndGetSetPointVariable(dev) #indigo.variables[int(dev.pluginProps.get(u"SetPointVariable", ""))]
                    setpointVariableValue = float(setpointVariable.value)
                    if newSetpoint != setpointVariableValue:
                        indigo.variable.updateValue(setpointVariable, str(newSetpoint))
                        setpointVariable.refreshFromServer()

                self._runHVACLogic(indigo.devices[dev.id])
        else:
            # Else log failure but do NOT update state on Indigo Server.
            indigo.server.log(u"send \"%s\" %s to %.1f° failed" % (dev.name, logActionName, newSetpoint), isError=True)

    ########################################
    def startup(self):
        self.debugLog(u"startup called")
        self.debugLog(u"Subscribing To Changes")
        indigo.devices.subscribeToChanges()
        indigo.variables.subscribeToChanges()

    def shutdown(self):
        self.debugLog(u"shutdown called")

    ########################################

    # noinspection PyShadowingBuiltins
    def heaterDevicesList(self, filter="", valuesDict=None, typeId="", targetId=0):
        myArray = []

        if "useThermostatsAsPrimaryHeater" in valuesDict:
            self.debugLog(u"heaterDevicesList Run, use thermostats: " + str(valuesDict["useThermostatsAsPrimaryHeater"]))
            if valuesDict["useThermostatsAsPrimaryHeater"]:
                for dev in indigo.devices:
                    try:
                        if type(dev) is indigo.ThermostatDevice:
                            myArray.append((dev.id, dev.name))
                    except:
                        pass
                return myArray

        for dev in indigo.devices:
            try:
                if (type(dev) is indigo.ThermostatDevice) or (type(dev) is indigo.RelayDevice):
                    myArray.append((dev.id, dev.name))
            except:
                pass

        return myArray

    # noinspection PyShadowingBuiltins
    def thermostatOnOptionsList(self, filter="", valuesDict=None, typeId="", targetId=0):
        myArray = []

        for mode in kHvacModeEnumToStrMap:
            myArray.append((_lookupActionStrFromHvacMode(mode), _lookupActionStrFromHvacMode(mode)))
            #self.debugLog(u"kHvacMode: " + str(mode))

        # TODO: Cant seem to figure out how to set a default value for this?
        # if "thermostatOnOptions" not in valuesDict:
        #     valuesDict["thermostatOnOptions"] = "heat"
        #     self.debugLog("XXXXXXXXXXXXXXX")
        #
        # if "thermostatOffOptions" not in valuesDict:
        #     valuesDict["thermostatOffOptions"] = "off"
        #     self.debugLog("YYYYYYYYYYYYY")
        #
        # try:
        #     self.debugLog("============> thermostatOnOption: " + str(valuesDict["thermostatOnOptions"]))
        #     self.debugLog("============> thermostatOffOption: " + str(valuesDict["thermostatOffOptions"]))
        # except Exception, err:
        #     pass

        return myArray


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

            #TODO Implement validation of out of bounds and timeout values in Config Prefs Dialog


    def runConcurrentThread(self):
        try:
            while True:
                for dev in indigo.devices.iter("self"):
                    if not dev.enabled or not dev.configured:
                        #Updatechecker
                        self.updater.checkVersionPoll()
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
        #TODO: Implement validation of Device Configuration.
        validatedOk = True
        errorsDict = indigo.Dict()

        self.debugLog(u"Selected on mode: " + valuesDict["thermostatOnOptions"])
        self.debugLog(u"Selected on Key: " + str(_lookupHvacModeFromActionStr(valuesDict["thermostatOnOptions"])))

        indigo.server.log("Number of primaryHeaterDevices selected: " + str(len(valuesDict["primaryHeaterDevices"])))
        if len(valuesDict["primaryHeaterDevices"]) < 1:
            errorsDict["primaryHeaterDevices"] = "You have to select minimum one heater"
            validatedOk = False

        if validatedOk:
            return True, valuesDict
        else:
            return False, valuesDict, errorsDict


    ########################################
    def deviceStartComm(self, dev):
        # Called when communication with the hardware should be established.
        # Here would be a good place to poll out the current states from the
        # thermostat. If periodic polling of the thermostat is needed (that
        # is, it doesn't broadcast changes back to the plugin somehow), then
        # consider adding that to runConcurrentThread() above.

        #self._refreshStatesFromHardware(dev, True, True)
        self.debugLog(u"-- deviceStartComm V:002.33--")

        newProps = dev.pluginProps

        self.debugLog(u"khvacmode for thermostat:" + newProps.get("thermostatOnOptions", ""))
        self.debugLog(u"khvacmode for thermostat:" + _lookupActionStrFromHvacMode(newProps.get("thermostatOnOptions", "")))

        #Handling backwards compatibility setting new prop to default: Devices.
        try:
            test = int(newProps.get("sensorInputOptions", ""))
        except Exception, err:
            newProps["sensorInputOptions"] = 0
            dev.replacePluginPropsOnServer(newProps)

        self.debugLog(u"Number of temperature sensors: " + str(len(self._getTemperatureSensorsIdsInVirtualDevice(dev))))
        #self._changeTempSensorCount(dev, len(self._getTemperatureSensorsIdsInVirtualDevice(dev)))
        newProps["NumTemperatureInputs"] = len(self._getTemperatureSensorsIdsInVirtualDevice(dev))

        self.debugLog(u"Number of humidity sensors: " + str(len(self._getHumiditySensorsIdsInVirtualDevice(dev))))
        #self._changeHumiditySensorCount(dev, len(self._getHumiditySensorsIdsInVirtualDevice(dev)))
        newProps["NumHumidityInputs"] = len(self._getHumiditySensorsIdsInVirtualDevice(dev))

        self.debugLog("Number of primary Heater Devices: " + str(len(newProps.get("primaryHeaterDevices", ""))))

        # Check to see if we are using any devices that supports HVAC opMode and Need Epuipment status
        if len(newProps.get("primaryHeaterDevices", "")) > 0 or len(newProps.get("secondaryHeaterDevices", "")) > 0 or len(newProps.get("acHeatPumpDevices", "")) > 0 or len(newProps.get("ventilationDevices", "")):
            newProps["SupportsHvacOperationMode"] = True
            newProps["ShowCoolHeatEquipmentStateUI"] = True
        else:
            newProps["SupportsHvacOperationMode"] = False
            newProps["ShowCoolHeatEquipmentStateUI"] = False

        # Check to se if we support Heat Set Point
        if len(newProps.get("primaryHeaterDevices", "")) > 0 or len(newProps.get("secondaryHeaterDevices", "")) > 0:
            newProps["SupportsHeatSetpoint"] = True
        else:
            newProps["SupportsHeatSetpoint"] = False

        # Check to se if we support Cool Set Point and Fan mode
        if len(newProps.get("acHeatPumpDevices", "")) > 0 or len(newProps.get("ventilationDevices", "")) > 0:
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

#       if newProps.get("configTemperatureDelta", ""):
#            dev.updateStateOnServer("temperatureDelta", float(newProps.get("configTemperatureDelta")))

        self._updateStatesFromProps(dev, newProps)

        self._getAllSensorsValuesNow(dev)
        #self._getPrimaryTemperatureVariablesIdsInVirtualDevice(dev)
        if self._validateAndGetSetPointVariable(dev):
            self.debugLog("Use variable setpoint link is true and variable selected")
            self._handleChangeSetpointAction(dev, float(self._validateAndGetSetPointVariable(dev).value), u"set heat setpoint from variable", u"setpointHeat")
                
        self._runHVACLogic(indigo.devices[dev.id])
        pass

    def _updateStatesFromProps(self, dev, props):
        self.debugLog("Update all States from Props")

        if "temperatureDelta" in dev.states:
            dev.updateStateOnServer("temperatureDelta", props.get("configTemperatureDelta", ""))
        if "mainThermostatMode" in dev.states:
            dev.updateStateOnServer("mainThermostatMode", props.get("configMainThermostatMode", ""))
        if "primaryHeaterOverride" in dev.states:
            dev.updateStateOnServer("primaryHeaterOverride", props.get("configPrimaryHeaterOverride", ""))
        if "maxAmbientTemperature" in dev.states:
            dev.updateStateOnServer("maxAmbientTemperature", props.get("configMaxAmbientTemperature", ""))
        if "minAmbientTemperature" in dev.states:
            dev.updateStateOnServer("minAmbientTemperature", props.get("configMinAmbientTemperature", ""))
        if "maxFloorTemperature" in dev.states:
            dev.updateStateOnServer("maxFloorTemperature", props.get("configMaxFloorTemperature", ""))
        if "minFloorTemperature" in dev.states:
            dev.updateStateOnServer("minFloorTemperature", props.get("configMinFloorTemperature", ""))
        if "noHeatOutsideTemperature" in dev.states:
            dev.updateStateOnServer("noHeatOutsideTemperature", props.get("configNoHeatOutsideTemperature", ""))
        if "noCoolOutsideTemperature" in dev.states:
            dev.updateStateOnServer("noCoolOutsideTemperature", props.get("configNoCoolOutsideTemperature", ""))
        if "outsideTempComp" in dev.states:
            dev.updateStateOnServer("outsideTempComp", props.get("configOutsideTempComp", ""))
        if "outsideHumComp" in dev.states:
            dev.updateStateOnServer("outsideHumComp", props.get("configOutsideHumComp", ""))
        if "primaryVentilationMode" in dev.states:
            dev.updateStateOnServer("primaryVentilationMode", props.get("configPrimaryVentilationMode", ""))
        if "dimmableVentilator" in dev.states:
            dev.updateStateOnServer("dimmableVentilator", props.get("configDimmableVentilator", ""))
        if "considerOutsideHumFanOff" in dev.states:
            dev.updateStateOnServer("considerOutsideHumFanOff", props.get("configConsiderOutsideHumFanOff", ""))
        if "humidityOff" in dev.states:
            dev.updateStateOnServer("humidityOff", props.get("configHumidityOff", ""))
        if "humidityStep1" in dev.states:
            dev.updateStateOnServer("humidityStep1", props.get("configHumidityStep1", ""))
        if "humidityStep2" in dev.states:
            dev.updateStateOnServer("humidityStep2", props.get("configHumidityStep2", ""))
        if "humidityStep3" in dev.states:
            dev.updateStateOnServer("humidityStep3", props.get("configHumidityStep3", ""))
        if "humidityStep4" in dev.states:
            dev.updateStateOnServer("humidityStep4", props.get("configHumidityStep4", ""))
        if "tempStep1" in dev.states:
            dev.updateStateOnServer("tempStep1", props.get("configTempStep1", ""))
        if "tempStep2" in dev.states:
            dev.updateStateOnServer("tempStep2", props.get("configTempStep2", ""))
        if "tempStep3" in dev.states:
            dev.updateStateOnServer("tempStep3", props.get("configTempStep3", ""))
        if "tempStep4" in dev.states:
            dev.updateStateOnServer("tempStep4", props.get("configTempStep4", ""))
        if "fanSpeedStep1" in dev.states:
            dev.updateStateOnServer("fanSpeedStep1", props.get("configFanSpeedStep1", ""))
        if "fanSpeedStep2" in dev.states:
            dev.updateStateOnServer("fanSpeedStep2", props.get("configFanSpeedStep2", ""))
        if "fanSpeedStep3" in dev.states:
            dev.updateStateOnServer("fanSpeedStep3", props.get("configFanSpeedStep3", ""))
        if "fanSpeedStep4" in dev.states:
            dev.updateStateOnServer("fanSpeedStep4", props.get("configFanSpeedStep4", ""))

    def deviceStopComm(self, dev):
        # Called when communication with the hardware should be shutdown.
        pass

    def _getSensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()

        if self._usePrimaryTemperatureSensors(dev): #dev.pluginProps.get("primaryTemperatureSensors", ""):
            for sens in (dev.pluginProps["primaryTemperatureSensors"]):
                #self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))

        if self._usePrimaryTemperatureVariable(dev):
            for sens in (dev.pluginProps["primaryTemperatureVariables"]):
                #self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))

        if dev.pluginProps.get("floorTemperatureSensors", ""):
            sensorDevices.append(int(dev.pluginProps["floorTemperatureSensors"]))

        if dev.pluginProps.get("outsideTemperatureSensors", ""):
            sensorDevices.append(int(dev.pluginProps["outsideTemperatureSensors"]))

        if dev.pluginProps.get("outsideHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["outsideHumiditySensors"]))

        if dev.pluginProps.get("optionalHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["optionalHumiditySensors"]))

        if dev.pluginProps.get("ambientHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["ambientHumiditySensors"]))

        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices

    def _getHumiditySensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()

        if dev.pluginProps.get("outsideHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["outsideHumiditySensors"]))

        if dev.pluginProps.get("optionalHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["optionalHumiditySensors"]))

        if dev.pluginProps.get("ambientHumiditySensors", ""):
            sensorDevices.append(int(dev.pluginProps["ambientHumiditySensors"]))

        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices

    def _getTemperatureSensorsIdsInVirtualDevice(self, dev):
        sensorDevices = indigo.List()


        if self._usePrimaryTemperatureSensors(dev): #dev.pluginProps.get("primaryTemperatureSensors", ""):
            for sens in (dev.pluginProps["primaryTemperatureSensors"]):
                self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))
            #sensorDevices.append(int(dev.pluginProps["temperatureSensor"]))

        if self._usePrimaryTemperatureVariable(dev):
            for sens in (dev.pluginProps["primaryTemperatureVariables"]):
                #self.debugLog("TemperatureSensor ID: " + sens)
                sensorDevices.append(int(sens))


        if dev.pluginProps.get("floorTemperatureSensors", ""):
            sensorDevices.append(int(dev.pluginProps["floorTemperatureSensors"]))

        if dev.pluginProps.get("outsideTemperatureSensors", ""):
            sensorDevices.append(int(dev.pluginProps["outsideTemperatureSensors"]))



        #self.debugLog(u"Sensor Device List: " + str(sensorDevices))
        return sensorDevices

    def _validateAndGetSetPointVariable(self, dev):
        if dev.pluginProps.get(u"useVariableSetPoint", "") and dev.pluginProps.get(u"SetPointVariable", ""):
            self.debugLog("Use variable setpoint link is true and variable selected")
            setpointVariable = indigo.variables[int(dev.pluginProps.get(u"SetPointVariable", ""))]
            try:
                value = float(setpointVariable.value)
                return setpointVariable
            except Exception, err:
                self.errorLog(u'Set Point Variable is not valid! Turning OFF Thermostat')
                indigo.thermostat.setHvacMode(dev, value=indigo.kHvacMode.Off)
                #This leads to infinite loop condition: self._handleChangeSetpointAction(dev, 0.0, u"set heat setpoint ERROR variable", u"setpointHeat")
                dev.updateStateOnServer(u"setpointHeat", 0.0, uiValue="%.1f°" % 0.0)
                return False
        else:
            return False

    def _usePrimaryTemperatureVariable(self, dev):
        if dev.pluginProps.get("primaryTemperatureVariables", "") and int(dev.pluginProps.get("sensorInputOptions", "")) != 0:
            return True
        else:
            return False


    def _usePrimaryTemperatureSensors(self, dev):
        if dev.pluginProps.get("primaryTemperatureSensors", "") and int(dev.pluginProps.get("sensorInputOptions", "")) != 1:
            return True
        else:
            return False


    def _handleChangeTemperatureSensors(self, thermostatDev, sensorDev):
        self.debugLog(u"************************** handleChangeTemperatureSensors *************************************")
        self.debugLog(u"*************************** " + str(sensorDev.name) + u" **************************************")
        self.debugLog(u"Sensor is of type = " + str(type(sensorDev)))

        if type(sensorDev) is indigo.Variable:
            #Check first to see if we got a sensorValue
            if sensorDev.value is None:
                #No sensor value, error wrong or not sensor
                self.errorLog(u"ERROR: Variable: " + str(sensorDev.name) + u" ,has no value. Please remove sensor from list.")
                return
        else:
            #Check first to see if we got a sensorValue
            if sensorDev.sensorValue is None:
                #No sensor value, error wrong or not sensor
                self.errorLog(u"ERROR: Sensor: " + str(sensorDev.name) + u" ,has no sensor value. Please remove sensor from list.")
                return

        # Temperature sensors
        if self._usePrimaryTemperatureSensors(thermostatDev): #thermostatDev.pluginProps.get("primaryTemperatureSensors", ""):
             for sens in (thermostatDev.pluginProps["primaryTemperatureSensors"]):
                if sensorDev.id == int(sens):
                    tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(sens)) + 1
                    thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%.1f°" % sensorDev.sensorValue)

        # Temperature Variable
        if self._usePrimaryTemperatureVariable(thermostatDev):
            for sens in (thermostatDev.pluginProps["primaryTemperatureVariables"]):
                if sensorDev.id == int(sens):
                    try:
                        tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(sens)) + 1
                        thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.value, uiValue="%.1f°" % float(sensorDev.value))
                    except Exception, err:
                        self.errorLog(u'Temperature Variable is not valid! Ignoring value')
                        tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(sens)) + 1
                        thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), -999, uiValue="%.1f°" % float(-999))

        if thermostatDev.pluginProps.get("floorTemperatureSensors", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["floorTemperatureSensors"]):
                tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["floorTemperatureSensors"])) + 1
                thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%.1f°" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("outsideTemperatureSensors", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["outsideTemperatureSensors"]):
                tempInputIndex = self._getTemperatureSensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["outsideTemperatureSensors"])) + 1
                thermostatDev.updateStateOnServer(u"temperatureInput" + str(tempInputIndex), sensorDev.sensorValue, uiValue="%.1f°" % sensorDev.sensorValue)

        # Humidity sensors
        if thermostatDev.pluginProps.get("outsideHumiditySensors", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["outsideHumiditySensors"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["outsideHumiditySensors"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="%.1f°" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("optionalHumiditySensors", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["optionalHumiditySensors"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["optionalHumiditySensors"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="%.1f°" % sensorDev.sensorValue)

        if thermostatDev.pluginProps.get("ambientHumiditySensors", ""):
            if sensorDev.id == int(thermostatDev.pluginProps["ambientHumiditySensors"]):
                humInputIndex = self._getHumiditySensorsIdsInVirtualDevice(thermostatDev).index(int(thermostatDev.pluginProps["ambientHumiditySensors"])) + 1
                thermostatDev.updateStateOnServer(u"humidityInput" + str(humInputIndex), sensorDev.sensorValue, uiValue="* %.1f%%" % sensorDev.sensorValue)


    def deviceUpdated(self, origDev, newDev):
        indigo.PluginBase.deviceUpdated(self, origDev, newDev)


        for dev in indigo.devices.iter("self"):
            if not dev.enabled or not dev.configured:
                continue

            if newDev.id in  self._getSensorsIdsInVirtualDevice(dev):
                self.debugLog("DeviceUpdate for device:" + dev.name + " Of Type: " + dev.deviceTypeId + " For Sensor: " + newDev.name + " With Value: " + str(newDev.sensorValue))
                self._handleChangeTemperatureSensors(dev, newDev)
                self._runHVACLogic(dev)

    def variableUpdated(self, origVar, newVar):
         for dev in indigo.devices.iter("self"):
            if not dev.enabled or not dev.configured:
                continue

            if newVar.id in self._getPrimaryTemperatureVariablesIdsInVirtualDevice(dev):
                self.debugLog("VariableUpdate for device:" + dev.name + " Of Type: " + dev.deviceTypeId + " For variable: " + newVar.name + " With Value: " + str(newVar.value))
                self._handleChangeTemperatureSensors(dev, newVar)
                self._runHVACLogic(dev)

            self.debugLog(u"useVariableSetPoint: " + str(dev.pluginProps.get(u"useVariableSetPoint", "")))
            self.debugLog(u"SetPointVariable: " + str(dev.pluginProps.get(u"SetPointVariable", "")))

            if self._validateAndGetSetPointVariable(dev):
            #if dev.pluginProps.get(u"useVariableSetPoint", "") and dev.pluginProps.get(u"SetPointVariable", ""):
                self.debugLog("Use variable setpoint link is true and variable selected")
                setpointVar = self._validateAndGetSetPointVariable(dev)
                if newVar.id == setpointVar.id: #int(dev.pluginProps.get(u"SetPointVariable", "")):
                    newSetpoint = float(setpointVar.value)
                    self._handleChangeSetpointAction(dev, newSetpoint, u"set heat setpoint from variable", u"setpointHeat")


    def _getPrimaryTemperatureVariablesIdsInVirtualDevice(self, dev):
        tempVariables = indigo.List()
        #self.debugLog(u"_________________------------------primaryTemperatureVariables ID--------------------________________")
        if self._usePrimaryTemperatureVariable(dev):
            for tempVariable in (dev.pluginProps["primaryTemperatureVariables"]):
                #var = indigo.variables[int(tempVariable)]
                #self.debugLog(u"TemperatureVariable ID: " + str(tempVariable) +  u" TemperatureVariable Name: " + str(var.name) + u" TemperatureVariable Value: " + str(var.value))
                tempVariables.append(int(tempVariable))
        return tempVariables

    def _getAllSensorsValuesNow(self, dev):
        for sensorId in self._getSensorsIdsInVirtualDevice(dev):
            if sensorId in indigo.devices:
                self._handleChangeTemperatureSensors(dev, indigo.devices[sensorId])
            if sensorId in indigo.variables:
                self._handleChangeTemperatureSensors(dev, indigo.variables[sensorId])



    def _getDeviceIdListFromProp(self, deviceProp, virDev):
        devList = []
        if virDev.pluginProps.get(deviceProp, ""):
            for sens in (virDev.pluginProps[deviceProp]):
                devList.append(int(sens))
                #TODO: can be var og dev!
                #self.debugLog(indigo.devices[int(sens)].name)

        return devList

    def _runHVACLogic(self, virDev):
        # Getting all the devices
        self.debugLog("=============== Running HVAC Logic ================")
        self.debugLog("Getting all the devices")

        # Temperature sensors
        self.debugLog("Temperature Sensors:")
        primaryTemperatureSensors = self._getDeviceIdListFromProp("primaryTemperatureSensors", virDev)
        if self._usePrimaryTemperatureVariable(virDev):
            primaryTemperatureSensors += (self._getDeviceIdListFromProp("primaryTemperatureVariables", virDev))

        self.debugLog(str(primaryTemperatureSensors))

        floorTemperatureSensors = self._getDeviceIdListFromProp("floorTemperatureSensors", virDev)
        outsideTemperatureSensors = self._getDeviceIdListFromProp("outsideTemperatureSensors", virDev)

        # Humidity sensors
        self.debugLog("Humidity Sensors:")
        outsideHumiditySensors = self._getDeviceIdListFromProp("outsideHumiditySensors", virDev)
        optionalHumiditySensors = self._getDeviceIdListFromProp("optionalHumiditySensors", virDev)
        ambientHumiditySensors = self._getDeviceIdListFromProp("ambientHumiditySensors", virDev)

        # HVAC Devices
        self.debugLog("HVAC Devices:")
        acHeatPumpDevices = self._getDeviceIdListFromProp("acHeatPumpDevices", virDev)
        primaryHeaterDevices = self._getDeviceIdListFromProp("primaryHeaterDevices", virDev)
        secondaryHeaterDevices = self._getDeviceIdListFromProp("secondaryHeaterDevices", virDev)
        ventilationDevices = self._getDeviceIdListFromProp("ventilationDevices", virDev)

        # Settings
        configTemperatureDelta = False
        self.debugLog("Settings:")
        if virDev.pluginProps.get("configTemperatureDelta", ""):
            configTemperatureDelta = float(virDev.states["temperatureDelta"])
            self.debugLog("TemperatureDelta: " + str(configTemperatureDelta))

        self.debugLog("Cool Set Point: " + str(virDev.coolSetpoint))
        self.debugLog("Heat Set Point: " + str(virDev.heatSetpoint))
    #		self.debugLog("hvacOperationMode: " + str(_lookupActionStrFromHvacMode(virDev.states["hvacOperationMode"])))
    #		self.debugLog("hvacOperationMode: " + str(virDev.states["hvacOperationMode"]))
        self.debugLog("hvacOperationMode: " + str(virDev.hvacMode))
        self.debugLog("fanMode: " + str(virDev.fanMode))
        self.debugLog("=============== Done Getting Devices and Settings ================")

        if virDev.hvacMode == indigo.kHvacMode.Off:
            self._turnOffAllHVACDevices(virDev)
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        elif virDev.hvacMode == indigo.kHvacMode.Cool:
            self._turnOffAllHVACDevices(virDev)
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        elif virDev.hvacMode == indigo.kHvacMode.Heat:
            self._turnOnDevicesInDeviceIdList(primaryHeaterDevices, virDev)
            # TODO For booster functionality, must implement
            #self._turnOnDevicesInDeviceIdList(secondaryHeaterDevices)
            virDev.updateStateOnServer("hvacHeaterIsOn", True)
        elif virDev.hvacMode == indigo.kHvacMode.HeatCool:
            self._heat(virDev, primaryHeaterDevices, primaryTemperatureSensors, secondaryHeaterDevices,
                       floorTemperatureSensors, outsideTemperatureSensors)
            #self._heat(virDev, primaryHeaterDevices, temperatureSensor, None, None, None)

        return True



            #indigo.kHvacMode.Cool				: u"cool",
            #indigo.kHvacMode.Heat				: u"heat",
            #indigo.kHvacMode.HeatCool			: u"auto",
            #indigo.kHvacMode.Off				: u"off",
            #indigo.kHvacMode.ProgramHeat		: u"program heat",
            #indigo.kHvacMode.ProgramCool		: u"program cool",
            #indigo.kHvacMode.ProgramHeatCool

    def _heat(self, virDev, primaryHeaterDevices, primaryTemperatureSensors, secondaryHeaterDevices,
              floorTemperatureSensors, outsideTemperatureSensors):
        # Heater logic
        heaters = primaryHeaterDevices
        sensorAvgTemp = self._avgSensorValues(virDev, primaryTemperatureSensors)

        if not sensorAvgTemp:
            # No valid sensor data, turning off all heaters'
            # TODO: Notifications
            self.errorLog(virDev.name + u": NO VALID SENSOR DATA: Turning Off ALL Heaters and Thermostat!")
            self._turnOffDevicesInDeviceIdList(heaters, virDev)
            self.debugLog(u"Heaters Off")

            virDev.updateStateOnServer("hvacHeaterIsOn", False)
            indigo.thermostat.setHvacMode(virDev, value=indigo.kHvacMode.Off)
            return False


        setTemp = virDev.heatSetpoint
        deltaTemp = float(virDev.states["temperatureDelta"])

        self.debugLog(u"********* Heat Logic Run for: " + virDev.name)
        self.debugLog(u"Number of Heaters: " + str(len(heaters)))
        self.debugLog(u"sensorAvgTemp: " + str(sensorAvgTemp))
        self.debugLog(u"Set Temp: " + str(setTemp))
        self.debugLog(u"Delta Temp: " + str(deltaTemp))

        if (sensorAvgTemp < (setTemp - deltaTemp)) and not self._isAllDevicesInDeviceIdListOn(heaters, virDev):
            self._turnOnDevicesInDeviceIdList(heaters, virDev)
            self.debugLog(u"Heaters On")
            virDev.updateStateOnServer("hvacHeaterIsOn", True)
        elif (sensorAvgTemp > (setTemp + deltaTemp)) and self._isAllDevicesInDeviceIdListOn(heaters, virDev):
            self._turnOffDevicesInDeviceIdList(heaters, virDev)
            self.debugLog(u"Heaters Off")
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        else:
            self.debugLog(u"In delta or set")
            if self._isAllDevicesInDeviceIdListOn(heaters, virDev):
                virDev.updateStateOnServer("hvacHeaterIsOn", True)
            else:
                virDev.updateStateOnServer("hvacHeaterIsOn", False)

        #Saftey check
        if sensorAvgTemp > (setTemp + deltaTemp + 1):
            self.debugLog(u"Too warm, turning off heaters")
            self._turnOffDevicesInDeviceIdList(heaters, virDev)
            self.debugLog(u"Heaters Off")
            virDev.updateStateOnServer("hvacHeaterIsOn", False)
        elif sensorAvgTemp < (setTemp - deltaTemp - 1):
            self.debugLog(u"Too cold, turning on heaters")
            self._turnOnDevicesInDeviceIdList(heaters, virDev)
            self.debugLog(u"Heaters On")
            virDev.updateStateOnServer("hvacHeaterIsOn", True)

    def _avgSensorValues(self, virDev, sensors):
        count = 0
        totalTemp = 0

        self.debugLog("Sensor Values to average:")
        for sens in sensors:
            if self._validateSensorValue(sens):
                if int(sens) in indigo.devices:
                    self.debugLog(str(indigo.devices[int(sens)].sensorValue))
                    count += 1
                    totalTemp += indigo.devices[int(sens)].sensorValue
                if int(sens) in indigo.variables:
                    self.debugLog(str(indigo.variables[int(sens)].value))
                    count += 1
                    totalTemp += float(indigo.variables[int(sens)].value)
            else:
                #TODO Display Error in ui value, would be nice if it could be shown in red, NO: http://forums.indigodomo.com/viewtopic.php?f=108&t=12752
                virDev.updateStateOnServer(u"temperatureInput" + str(count + 1), -999, uiValue="-999")
                #virDev.updateStateOnServer(u"temperatureInput" + str(count + 1), indigo.devices[int(sens)].sensorValue, uiValue="%.1f°" % indigo.devices[int(sens)].sensorValue)
                pass

        if count > 0:
            return totalTemp/count
        else:
            return False

    def _validateSensorValue(self, sensorId):
        timeoutValidationOk = False
        maxValueValidationOk = False
        minValueValidationOk = False
        sensorLastChanged = datetime.datetime.now()
        sensorValue = False
        sensorName = ""

        self.debugLog(u"===============> sensorId=" + str(sensorId) + u" Type=" + str(type(sensorId)))

        if sensorId in indigo.devices:
            self.debugLog(str(indigo.devices[sensorId].name) + u" Value: " + str(indigo.devices[sensorId].sensorValue) + u" Last changed:" + str(indigo.devices[sensorId].lastChanged))
            #Getting sensor values
            sensorLastChanged = indigo.devices[sensorId].lastChanged
            sensorValue = indigo.devices[sensorId].sensorValue
            sensorName = str(indigo.devices[sensorId].name)

        if sensorId in indigo.variables:
            self.debugLog(str(indigo.variables[sensorId].name) + u" Value: " + str(indigo.variables[sensorId].value) + u" Last changed:" + u"Variables DO NOT HAVE a last changed value!")
            #Getting sensor values
            #TODO: Document: Variables do not have a last changed value so cannot check this.
            #NOTE: Variables do not have a last changed value so cannot check this.
            sensorLastChanged = datetime.datetime.now() #indigo.variables[sensorId].lastChanged
            try:
                sensorValue = float(indigo.variables[sensorId].value)
            except Exception, err:
                self.errorLog(u'Temperature Variable is not valid!')
                return False

            sensorName = str(indigo.variables[sensorId].name)


        self.debugLog(u"Sensor to validate last updated on: " + str(sensorLastChanged))
        self.debugLog(u"Sensor to validate value: " + str(sensorValue))

        #Defining validation variables with defaults
        notOlderThenMinutes = 120
        ignoreValuesLargerThen = 60.0
        ignoreValuesLessThen = -40.0

        #self.debugLog("ignoreValuesOlderThen: " + self.pluginPrefs.get("ignoreValuesOlderThen", ""))

        #Getting timeout value from configuration prefs
        if self.pluginPrefs.get("ignoreValuesOlderThen", ""):
            try:
                notOlderThenMinutes = int(self.pluginPrefs.get("ignoreValuesOlderThen", ""))
            except Exception, err:
                self.errorLog(u"ERROR in ignore Values Older Then: %s. Using defaults: %s" % (str(err), str(notOlderThenMinutes)))

        self.debugLog(u"ignoreValuesOlderThen Set To: " + str(notOlderThenMinutes))

        lastChangedMaxAge = datetime.datetime.now() - datetime.timedelta(minutes = notOlderThenMinutes)
        self.debugLog(str(lastChangedMaxAge))

        #Validating sensor last changed timeout.
        if sensorLastChanged < lastChangedMaxAge:
            self.errorLog(str(sensorName) + " Value: " + str(sensorValue) + " Last changed:" + str(sensorLastChanged))
            self.errorLog(u"OLD Value! Sensor value is older then " + str(notOlderThenMinutes) + " Minutes")
            timeoutValidationOk = False
        else:
            self.debugLog(u"sensor last changed newer then two hours")
            timeoutValidationOk = True

        #Getting max value from configuration prefs
        if self.pluginPrefs.get("ignoreValuesLargerThen", ""):
            try:
                ignoreValuesLargerThen = float(self.pluginPrefs.get("ignoreValuesLargerThen", ""))
            except Exception, err:
                self.errorLog(u"ERROR in ignore Values Larger Then: %s. Using defaults: %s" % (str(err), str(ignoreValuesLargerThen)))

        self.debugLog(u"ignoreValuesLargerThen Set To: " + str(ignoreValuesLargerThen) )

        #Validating max value boundary.
        if sensorValue > ignoreValuesLargerThen:
            self.errorLog(str(sensorName) + " Value: " + str(sensorValue) + " Last changed:" + str(sensorLastChanged))
            self.errorLog("OUT OF BOUNDS Value! Sensor value is larger then " + str(ignoreValuesLargerThen) + "!")
            maxValueValidationOk = False
        else:
            self.debugLog(u"Sensor value is less then max allowed value, Ok")
            maxValueValidationOk = True


        #Getting min value from configuration prefs
        if self.pluginPrefs.get("ignoreValuesLessThen", ""):
            try:
                ignoreValuesLessThen = float(self.pluginPrefs.get("ignoreValuesLessThen", ""))
            except Exception, err:
                self.errorLog(u"ERROR in ignore Values Less Then: %s. Using defaults: %s" % (str(err), str(ignoreValuesLessThen)))

        self.debugLog(u"ignoreValuesLessThen Set To: " + str(ignoreValuesLessThen) )

        #Validating min value boundary.
        if sensorValue < ignoreValuesLessThen:
            self.errorLog(str(sensorName) + u" Value: " + str(sensorValue) + u" Last changed:" + str(sensorLastChanged))
            self.errorLog(u"OUT OF BOUNDS Value! Sensor value is less then " + str(ignoreValuesLessThen) + "!")
            minValueValidationOk = False
        else:
            self.debugLog(u"Sensor value is larger then minimum allowed value, Ok")
            minValueValidationOk = True

        #TODO: Implement comparison check. If one of multiple values is very different from the others, its probably wrong.
        #TODO: Implement notifications on error such as these.

        return  timeoutValidationOk and maxValueValidationOk and minValueValidationOk

    def _isAllDevicesInDeviceIdListOn(self, deviceIdList ,virDev):
        isOn = False
        self.debugLog(u"Check if all dev in list is on:")

        for dev in deviceIdList:
            self.debugLog(indigo.devices[int(dev)].name)

            # self.debugLog(u"type: " + str(type(indigo.devices[int(dev)])))
            if type(indigo.devices[int(dev)]) is indigo.ThermostatDevice:
                #self.debugLog(u"IS Thermostat!")

                self.debugLog("------------->>>>>>>> hvacOperationMode of controlled thermostat: " + str(_lookupActionStrFromHvacMode(indigo.devices[int(dev)].states["hvacOperationMode"])))

                #if indigo.devices[int(dev)].heatIsOn: #This is the bug, this only checks if the other thermostat is heating not if its mode is on/Heat
                #if not indigo.devices[int(dev)].states["hvacOperationModeIsOff"]: #This is better check that checks on the actual mode, not what the thermostat is doing.
                #Above new bug when using custom states for on/off
                if indigo.devices[int(dev)].states["hvacOperationMode"] == _lookupHvacModeFromActionStr(virDev.pluginProps.get("thermostatOnOptions", "on")):
                    isOn = True
                    self.debugLog(u"isOn")

            else:
                self.debugLog(indigo.devices[int(dev)].name + u" On State: " + str(indigo.devices[int(dev)].onState))
                if indigo.devices[int(dev)].onState:
                    isOn = True
                    self.debugLog(u"isOn")

        self.debugLog(u"isOn: " + str(isOn))
        return isOn

    def _turnOffDevicesInDeviceIdList(self, deviceIdList, virDev):
        self.debugLog(u"Turning Off:")

        for dev in deviceIdList:
            self.debugLog(indigo.devices[int(dev)].name)

            if type(indigo.devices[int(dev)]) is indigo.ThermostatDevice:
                #indigo.thermostat.setHvacMode(int(dev), value=indigo.kHvacMode.Off)
                indigo.thermostat.setHvacMode(int(dev), value=_lookupHvacModeFromActionStr(virDev.pluginProps.get("thermostatOffOptions", "off")))
            else:
                indigo.device.turnOff(int(dev))


    def _turnOnDevicesInDeviceIdList(self, deviceIdList, virDev):
        self.debugLog("Turning On:")

        for dev in deviceIdList:
            self.debugLog(indigo.devices[int(dev)].name)
            if type(indigo.devices[int(dev)]) is indigo.ThermostatDevice:
                #if virDev.pluginProps.get("thermostatOnOptions", ""):
                indigo.thermostat.setHvacMode(int(dev), value=_lookupHvacModeFromActionStr(virDev.pluginProps.get("thermostatOnOptions", "heat")))
                #else:
                #    indigo.thermostat.setHvacMode(int(dev), value=indigo.kHvacMode.Heat)
            else:
                indigo.device.turnOn(int(dev))


    def _turnOffAllHVACDevices(self, virDev):
        if virDev.pluginProps.get("acHeatPumpDevices", ""):
            self._turnOffDevicesInDeviceIdList(virDev.pluginProps.get("acHeatPumpDevices"), virDev)
            
        if virDev.pluginProps.get("primaryHeaterDevices", ""):
             self._turnOffDevicesInDeviceIdList(virDev.pluginProps.get("primaryHeaterDevices"), virDev)

        if virDev.pluginProps.get("secondaryHeaterDevices", ""):
           self._turnOffDevicesInDeviceIdList(virDev.pluginProps.get("secondaryHeaterDevices"), virDev)

        if virDev.pluginProps.get("ventilationDevices", ""):
             self._turnOffDevicesInDeviceIdList(virDev.pluginProps.get("ventilationDevices"), virDev)


    ########################################
    # Thermostat Action callback
    ######################
    # Main thermostat action bottleneck called by Indigo Server.
    def actionControlThermostat(self, action, dev):
        value = None
        try:
            value = action.actionValue
        except Exception, err:
            pass

        self.debugLog(u"ACTION ===========> " + str(action))
        self.debugLog(u"Action Value===========> " + str(value))

        # I want to be able to change the setpoint in 0.5 increments with the UI arrows. So here is the hack
        # This hack will influence others trying to increment by 1. e.g. by using actions. But only for 1.
        # TODO: Figure out how to identify arrow clicks only
        if value == 1:
            value = 0.5

        ###### SET HVAC MODE ######
        if action.thermostatAction == indigo.kThermostatAction.SetHvacMode:
            self._handleChangeHvacModeAction(dev, action.actionMode)

        ###### SET FAN MODE ######
        elif action.thermostatAction == indigo.kThermostatAction.SetFanMode:
            self._handleChangeFanModeAction(dev, action.actionMode)

        ###### SET COOL SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.SetCoolSetpoint:
            newSetpoint = value
            self._handleChangeSetpointAction(dev, newSetpoint, u"change cool setpoint", u"setpointCool")

        ###### SET HEAT SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.SetHeatSetpoint:
            newSetpoint = value
            self._handleChangeSetpointAction(dev, newSetpoint, u"change heat setpoint", u"setpointHeat")

        ###### DECREASE/INCREASE COOL SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.DecreaseCoolSetpoint:
            #newSetpoint = dev.coolSetpoint - 0.5 #action.actionValue
            newSetpoint = dev.coolSetpoint - value
            #newSetpoint = action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"decrease cool setpoint", u"setpointCool")

        elif action.thermostatAction == indigo.kThermostatAction.IncreaseCoolSetpoint:
            #newSetpoint = dev.coolSetpoint + 0.5 #action.actionValue
            newSetpoint = dev.coolSetpoint + value
            #newSetpoint = action.actionValue
            self._handleChangeSetpointAction(dev, newSetpoint, u"increase cool setpoint", u"setpointCool")

        ###### DECREASE/INCREASE HEAT SETPOINT ######
        elif action.thermostatAction == indigo.kThermostatAction.DecreaseHeatSetpoint:
            #newSetpoint = dev.heatSetpoint - 0.5 #action.actionValue
            #newSetpoint = action.actionValue
            newSetpoint = dev.heatSetpoint - value
            self._handleChangeSetpointAction(dev, newSetpoint, u"decrease heat setpoint", u"setpointHeat")

        elif action.thermostatAction == indigo.kThermostatAction.IncreaseHeatSetpoint:
            #newSetpoint = dev.heatSetpoint + 0.5 #action.actionValue
            #newSetpoint = action.actionValue
            newSetpoint = dev.heatSetpoint + value
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
        valuesDict["primaryHeaterDevices"] = ""
        valuesDict["secondaryHeaterDevices"] = ""
        valuesDict["ventilationDevices"] = ""
        valuesDict["acHeatPumpDevices"] = ""
        valuesDict["autoLabel21"] = u"Test"
        self.debugLog(u"Clear pushed")

        return valuesDict


    def ClearTemperatureDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["primaryTemperatureSensors"] = ""
        valuesDict["floorTemperatureSensors"] = ""
        valuesDict["outsideTemperatureSensors"] = ""
        return valuesDict

    def ClearHumidityDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["ambientHumiditySensors"] = ""
        valuesDict["optionalHumiditySensors"] = ""
        valuesDict["outsideHumiditySensors"] = ""
        return valuesDict

    def ClearTemperatureVariablesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["primaryTemperatureVariables"] = ""
        return valuesDict

    def ClearHumidityVariablesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["ambientHumidityVariables"] = ""
        return valuesDict

    def ClearFanDevicesPressed(self, valuesDict, typeId, devId):
        #self.debugLog(u"Values Dict: " + str(valuesDict))
        valuesDict["fanDevice"] = ""
        return valuesDict

    def useThermostatsAsPrimaryHeater(self, valuesDict, typeId, devId):
        #valuesDict["autoLabel21"] = u"test"
        self.debugLog(u"heaterOptionsSelected")
        return valuesDict

    #Updatecheker
    def checkForUpdates(self):
        indigo.server.log(u"Manually checking for updates")
        self.updater.checkVersionNow()
