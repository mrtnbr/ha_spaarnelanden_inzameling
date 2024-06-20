"""Sensor component Spaarnelanden Inzameling"""

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import PERCENTAGE

from datetime import datetime, timedelta

from gazpacho import Soup

import logging
import json
import re

DOMAIN = "spaarnelanden_inzameling"

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S:%f'

CONTAINER_NUMBER = ''  # 'Nummer' van container op https://inzameling.spaarnelanden.nl/

SOURCE_URL = 'https://inzameling.spaarnelanden.nl/'
SEARCH_TAG = 'script'
SEARCH_PATTERN = 'var oContainerModel =(.*])'

TIME_BETWEEN_UPDATES = timedelta(minutes=10)
SENSOR_NAME = 'Spaarnelanden Inzameling (Container ' + CONTAINER_NUMBER + ')'

TRASH_TYPES = {
    'Papier': ['Papier', 'mdi:recycle'],
    'Pbd': ['Plastic, Blik en Drinkpakken', 'mdi:recycle'],
    'Rest': ['Restafval', 'mdi:delete-outline'],
    'Textiel': ['Textiel', 'mdi:recycle'],
    'Glas': ['Glas', 'mdi:recycle'],
    None: ['None', 'mdi:cloud-question']
}

FILLING_DEGREE_STATUSES = {
    1: 'Niet ingepland vandaag',
    2: 'Onbekend (2)',
    3: 'Ingepland'
}

_LOGGER = logging.getLogger(__name__)


def get_containerdata():
    try:
        containers_dictionary = {}

        _LOGGER.debug('Data scraping started: ' + datetime.today().strftime(DATETIME_FORMAT))

        soup = Soup.get(SOURCE_URL)

        _LOGGER.debug('Data scraping finished: ' + datetime.today().strftime(DATETIME_FORMAT))

        _LOGGER.debug('Processing scraped data started: ' + datetime.today().strftime(DATETIME_FORMAT))

        containers_json_decoded = \
            json.JSONDecoder().decode(
                re.search(
                    SEARCH_PATTERN, soup.find(SEARCH_TAG)[10].text
                ).group(1))

        for i in containers_json_decoded:
            if i['sRegistrationNumber'] == CONTAINER_NUMBER:
                containers_dictionary['filling_degree_status'] = FILLING_DEGREE_STATUSES[(i['iFillingDegreeStatus'])]
                containers_dictionary['filling_degree'] = (i['dFillingDegree'])
                containers_dictionary['latitude'] = (i['dLatitude'])
                containers_dictionary['longitude'] = (i['dLongitude'])
                containers_dictionary['registration_number'] = (i['sRegistrationNumber'])
                containers_dictionary['is_out_of_use'] = (i['bIsOutOfUse'])
                containers_dictionary['is_skipped'] = (i['bIsSkipped'])
                containers_dictionary['is_emptied_today'] = (i['bIsEmptiedToday'])
                containers_dictionary['date_last_emptied'] = datetime.strptime(i['sDateLastEmptied'], '%d-%m-%Y')
                containers_dictionary['container_product_id'] = (i['iContainerProductId'])
                containers_dictionary['product_name'] = (i['sProductName'])
                containers_dictionary['container_kind_name'] = (i['sContainerKindName'])
                containers_dictionary['datetime_last_check'] = datetime.now()
                break

        _LOGGER.debug('Processing scraped data finished: ' + datetime.today().strftime(DATETIME_FORMAT))

        return containers_dictionary
    except:
        _LOGGER.debug('Error getting data')
        return False


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug('Setup sensor')

    add_entities([ContainerSensor()])


class ContainerSensor(Entity):
    def __init__(self):
        """Initialize the sensor."""
        self._state = None

        self.containerdata = {
            'filling_degree_status': None,
            'filling_degree': None,
            'latitude': None,
            'longitude': None,
            'registration_number': None,
            'is_out_of_use': None,
            'is_skipped': None,
            'is_emptied_today': None,
            'date_last_emptied': None,
            'product_name': None,
            'container_kind_name': None,
            'datetime_last_check': None}

        self._icon = 'mdi:cloud-question'

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_NAME

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            'filling_degree_status': self.containerdata['filling_degree_status'],
            'filling_degree': self.containerdata['filling_degree'],
            'latitude': self.containerdata['latitude'],
            'longitude': self.containerdata['longitude'],
            'registration_number': self.containerdata['registration_number'],
            'is_out_of_use': self.containerdata['is_out_of_use'],
            'is_skipped': self.containerdata['is_skipped'],
            'is_emptied_today': self.containerdata['is_emptied_today'],
            'date_last_emptied': self.containerdata['date_last_emptied'],
            'product_name': self.containerdata['product_name'],
            'container_kind_name': self.containerdata['container_kind_name'],
            'datetime_last_check': self.containerdata['datetime_last_check']
            }

    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.debug('Updating containerdata started: ' + datetime.today().strftime(DATETIME_FORMAT))

        self.containerdata = get_containerdata()
        self._state = self.containerdata['filling_degree']
        self._icon = TRASH_TYPES[self.containerdata['product_name']][1]

        _LOGGER.debug('Updating containerdata finished: ' + datetime.today().strftime(DATETIME_FORMAT))
