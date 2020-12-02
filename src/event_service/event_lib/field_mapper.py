# Author:  Dlo Bagari
# created Date: 11-11-2019
from event_lib.const_values import ConstValues
from dateutil.parser import parse
from datetime import timezone

class FieldMapper:
    def __init__(self, settings):
        self._settings = settings

    def map(self, event):
        """
        Maps events fields to FBA fields and return a json file
        :param event: the event object
        :return: error_code, error_message, json_file
        """
        timestamp_object = parse(event["createdDateTime"])
        timestamp_object = timestamp_object.astimezone(tz=timezone.utc)
        timestamp = timestamp_object.isoformat()
        rim_json = {"timestamp": timestamp,
                    "type": "Authentication",
                    "entities": [],
                    "attributes": [{"type": "String", "name": "Time Stamp", "value": timestamp}]}
        
        subject = self.get_subject(event)
        if subject is not None:
            rim_json["subject"] = subject
        label = self.get_label(event)
        if label is not None:
            rim_json["labels"] = [label]
        source_event_id = self.get_source_event_id(event)
        if source_event_id is not None:
            rim_json["source_event_id"] = source_event_id
        roles = [self.get_app, self.user, self.domain, self.vendor, self.source_ip,
                 self.source_country, self.source_city, self.user_id, self.email_address, self.operating_system,
                 self.vendor_id, self.device_id]
        attributes = [self.browser_name, self.browser_version, self.device_name, self.event_id,
                      self.success, self.session_id_attribute, self.used_app_id,
                      self.is_interactive_sign_in, self.risk_details, self.risk_level_aggregated,
                      self.risk_level_duringSignIn, self.risk_state, self.trusted_sign_in
                      ]
        success = self.success(event)
        if success is not None and success["value"] == "false":
            rim_json["attributes"].append(self.reason(event))
        mfa = self.condition_access_status(event)
        if mfa is not None:
            for policy in mfa:
                rim_json["attributes"].append({"type": "String", "name": policy,
                                               "value": mfa[policy]})
        for role in roles:
            result = role(event)
            if result is not None:
                rim_json["entities"].append(result)
        for attr in attributes:
            result = attr(event)
            if result is not None:
                rim_json["attributes"].append(result)
        success = self.success(event)
        if success is not None and success["value"] is False:
            reason = self.reason(event)
            if reason is not None:
                rim_json["attributes"].append(reason)
        return rim_json

    def email_address(self, event):
        try:
            value = event["userPrincipalName"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Email", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def device_id(self, event):
        try:
            value = event["deviceDetail"]["deviceId"]
            if value == "" or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Device ID", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def vendor_id(self, event):
        try:
            value = event["resourceId"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Vendor ID", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def operating_system(self, event):
        try:
            value = event["deviceDetail"]["operatingSystem"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Operating System", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def get_subject(self, event):
        try:
            result = event["status"]["errorCode"]
            return f'Authentication:{"succeeded" if result == 0 else "Failed"} - {event["appDisplayName"]}'
        except KeyError:
            return None

    def get_source_event_id(self, event):
        try:
            return event["id"]
        except KeyError:
            return None

    def get_app(self, event):
        try:
            app = event["appDisplayName"]
            if app is None or (app is not None and app.lower() == "unknown"):
                return None
            return {"role": "App", "entities": [app.replace("'", "")]}
        except KeyError:
            return None

    def user_id(self, event):
        try:
            user_id = event["userId"]
            if user_id is None or (user_id is not None and user_id.lower() == "unknown"):
                return None
            return {"role": "User ID", "entities": [user_id]}
        except KeyError:
            return None

    def user(self, event):
        try:
            value = event["userDisplayName"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "User", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def domain(self, event):
        try:
            value = self._settings["tenant_name"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Domain", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def vendor(self, event):
        return {"role": "Vendor", "entities": [event["resourceDisplayName"]]}

    def source_ip(self, event):
        try:
            value = event["ipAddress"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source IP", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def source_country(self, event):
        try:
            value = event["location"]["countryOrRegion"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source Country", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def source_city(self, event):
        try:
            value = event["location"]["city"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source City", "entities": [value.replace("'", "")]}
        except KeyError:
            return None

    def browser_name(self, event):
        try:
            value = event["deviceDetail"]["browser"]

            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            value = value.split()[0]
            return {"type": "String", "name": "Browser Name", "value": value.replace("'", "").lower()}
        except KeyError:
            return None

    def browser_version(self, event):
        try:
            value = event["deviceDetail"]["browser"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            value = value.split()[1]
            return {"type": "String", "name": "Browser Version", "value": value.replace("'", "")}
        except KeyError:
            return None

    def device_name(self, event):
        try:
            value = event["clientAppUsed"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Device Type", "value": value.replace("'", "")}
        except KeyError:
            return None


    def event_id(self, event):
        try:
            value = event["id"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Event ID", "value": value.replace("'", "")}
        except KeyError:
            return None

    def success(self, event):
        try:
            value = "true" if event["status"]["errorCode"] == 0 else "false"
            if value is None:
                return None
            return {"type": "Boolean", "name": "Success", "value": value}
        except KeyError:
            return None

    def reason(self, event):
        try:
            value = event["status"]["failureReason"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Reason", "value": value.replace("'", "")}
        except KeyError:
            return None

    def session_id_attribute(self, event):
        try:
            value = event["correlationId"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Session ID", "value": value.replace("'", "")}
        except KeyError:
            return None

    def used_app_id(self, event):
        try:
            value = event["appId"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "App ID", "value": value.replace("'", "").lower()}
        except KeyError:
            return None

    def condition_access_status(self, event):
        mfa = None
        if event["conditionalAccessStatus"] != "notApplied":
            mfa = {}
            if len(event["appliedConditionalAccessPolicies"]) != 0:
                for policy in event["appliedConditionalAccessPolicies"]:
                    mfa[policy["displayName"]] = policy["result"]
        return mfa

    def is_interactive_sign_in(self, event):
        try:
            value = event["isInteractive"]
            return {"type": "String", "name": "Interactive SignIn", "value": str(value).lower()}
        except KeyError:
            return None

    def risk_details(self, event):
        try:
            value = event["riskDetail"]
            if value is None or (value is not None and value.lower() == "none"):
                return None
            return {"type": "String", "name": "Risk Detail", "value": str(value).lower()}
        except KeyError:
            return None

    def risk_level_aggregated(self, event):
        try:
            value = event["riskLevelAggregated"]
            if value is None or (value is not None and value.lower() == "none"):
                return None
            return {"type": "String", "name": "Risk Level Aggregated", "value": str(value).lower()}
        except KeyError:
            return None

    def risk_level_duringSignIn(self, event):
        try:
            value = event["riskLevelDuringSignIn"]
            if value is None or (value is not None and value.lower() == "none"):
                return None
            return {"type": "String", "name": "Risk Level During SignIn", "value": str(value).lower()}
        except KeyError:
            return None

    def risk_state(self, event):
        try:
            value = event["riskState"]
            if value is None or (value is not None and value.lower() == "none"):
                return None
            return {"type": "String", "name": "Risk State", "value": str(value).lower()}
        except KeyError:
            return None

    def get_label(self, event):
        result = self.success(event)
        if result is not None:
            return "success".upper() if result["value"] == "true" else "failure".upper()
        return None

    def trusted_sign_in(self, event):
        try:
            value = event["deviceDetail"]["trustType"]
            if value is None or (value is not None and value.lower() == "none"):
                return None
            return {"type": "String", "name": "Trusted SignIn", "value": str(value).lower()}
        except KeyError:
            return None
