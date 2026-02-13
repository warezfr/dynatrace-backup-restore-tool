"""Dynatrace API service for Managed environments"""
import requests
import logging
from typing import Optional, List, Dict
from ..core.config import settings

logger = logging.getLogger(__name__)

class DynatraceAPIService:
    """Interact with Dynatrace API for Managed environments"""
    
    def __init__(self, environment_url: str, api_token: str, insecure_ssl: bool = False):
        self.environment_url = environment_url.rstrip('/')
        self.api_token = api_token
        self.insecure_ssl = insecure_ssl
        self.base_url = f"{self.environment_url}/api/v2"
        
        # Session with auth
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Api-Token {api_token}",
            "Content-Type": "application/json",
        })
        
        if insecure_ssl:
            self.session.verify = False
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to Dynatrace"""
        try:
            response = self.session.get(
                f"{self.base_url}/environment/details",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                env_id = data.get("environmentId", "unknown")
                logger.info(f"Successfully connected to Dynatrace: {env_id}")
                return True, f"Connected to environment: {env_id}"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Connection failed: {error}")
                return False, f"Connection failed: {error}"
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False, f"Connection error: {str(e)}"
    
    def get_management_zones(self) -> tuple[bool, List[Dict], str]:
        """Get list of management zones"""
        try:
            response = self.session.get(
                f"{self.base_url}/managementZones",
                timeout=30
            )
            
            if response.status_code == 200:
                zones = response.json().get("values", [])
                logger.info(f"Found {len(zones)} management zones")
                return True, zones, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Failed to get management zones: {error}")
                return False, [], error
        except Exception as e:
            logger.error(f"Error getting management zones: {e}")
            return False, [], str(e)
    
    def get_dashboard_list(self, management_zone: Optional[str] = None) -> tuple[bool, List[Dict], str]:
        """Get list of dashboards"""
        try:
            params = {}
            if management_zone:
                params["filter"] = f"managementZone(\"{management_zone}\")"
            
            response = self.session.get(
                f"{self.base_url}/dashboards",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                dashboards = response.json().get("dashboards", [])
                logger.info(f"Found {len(dashboards)} dashboards")
                return True, dashboards, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Failed to get dashboards: {error}")
                return False, [], error
        except Exception as e:
            logger.error(f"Error getting dashboards: {e}")
            return False, [], str(e)
    
    def get_alerting_profiles(self, management_zone: Optional[str] = None) -> tuple[bool, List[Dict], str]:
        """Get list of alerting profiles"""
        try:
            params = {}
            if management_zone:
                params["filter"] = f"managementZone(\"{management_zone}\")"
            
            response = self.session.get(
                f"{self.base_url}/alertingProfiles",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                profiles = response.json().get("alertingProfiles", [])
                logger.info(f"Found {len(profiles)} alerting profiles")
                return True, profiles, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Failed to get alerting profiles: {error}")
                return False, [], error
        except Exception as e:
            logger.error(f"Error getting alerting profiles: {e}")
            return False, [], str(e)
    
    def get_slos(self, management_zone: Optional[str] = None) -> tuple[bool, List[Dict], str]:
        """Get list of SLOs"""
        try:
            params = {}
            if management_zone:
                params["filter"] = f"managementZone(\"{management_zone}\")"
            
            response = self.session.get(
                f"{self.base_url}/slo",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                slos = response.json().get("slo", [])
                logger.info(f"Found {len(slos)} SLOs")
                return True, slos, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Failed to get SLOs: {error}")
                return False, [], error
        except Exception as e:
            logger.error(f"Error getting SLOs: {e}")
            return False, [], str(e)
    
    def get_notification_channels(self) -> tuple[bool, List[Dict], str]:
        """Get list of notification integrations"""
        try:
            response = self.session.get(
                f"{self.base_url}/notifications",
                timeout=30
            )
            
            if response.status_code == 200:
                channels = response.json().get("notifications", [])
                logger.info(f"Found {len(channels)} notification channels")
                return True, channels, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Failed to get notifications: {error}")
                return False, [], error
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return False, [], str(e)
    
    def get_environment_info(self) -> tuple[bool, Dict, str]:
        """Get environment information"""
        try:
            response = self.session.get(
                f"{self.base_url}/environment/details",
                timeout=10
            )
            
            if response.status_code == 200:
                info = response.json()
                logger.info(f"Environment info retrieved")
                return True, info, "Success"
            else:
                error = response.json().get("error", {}).get("message", response.text)
                return False, {}, error
        except Exception as e:
            logger.error(f"Error getting environment info: {e}")
            return False, {}, str(e)

    def preflight_config_access(self, config_types: List[str]) -> tuple[bool, List[str]]:
        """Best-effort check for required read permissions per config type."""
        if not config_types or "all" in config_types:
            return True, []

        checks = {
            "alerting": self.get_alerting_profiles,
            "dashboards": self.get_dashboard_list,
            "slo": self.get_slos,
            "management_zone": self.get_management_zones,
            "notification": self.get_notification_channels,
        }

        errors: List[str] = []
        for config_type, check in checks.items():
            if config_type not in config_types:
                continue
            success, _, message = check()
            if not success:
                errors.append(f"{config_type}: {message}")

        return len(errors) == 0, errors
