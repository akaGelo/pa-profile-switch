import base64
import io
import logging
import sys
from threading import Thread

import pulsectl
from PIL import Image, ImageDraw, ImageFont
from pulsectl import pulsectl
from pystray import Icon, Menu, MenuItem

log = logging.getLogger("pa-profile-switch")
log.setLevel(logging.INFO)


class HeadphonesIndicator:
    __icon = base64.b64decode(
        "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")

    def __init__(self, card: pulsectl.PulseCardInfo) -> None:
        super().__init__()
        self.thread = None
        self.card = card
        self.description = self.card.proplist['device.description']

        self.tray_icon = Icon('test', self._create_image(card.profile_active.name), menu=self._create_menu(card))

    def _create_menu(self, card):
        items = []
        for profile in card.profile_list:
            is_active = '✓' if card.profile_active.description == profile.description else ''
            menu_item = MenuItem(f'{profile.name} {is_active}',
                                 lambda icon, item: self.__set_profile(icon, item))
            menu_item.profile = profile
            items.append(menu_item)
        menu = Menu(*items)
        return menu

    @staticmethod
    def _create_image(profile_name):
        image = Image.open(io.BytesIO(HeadphonesIndicator.__icon))
        dc = ImageDraw.Draw(image)
        font = ImageFont.truetype('DejaVuSans-Bold', 28)
        dc.text((24, 24),
                profile_name[0].upper(),  # Text
                (0, 0, 0), font=font)
        return image

    def start(self):
        self.thread = Thread(target=self.tray_icon.run)
        self.thread.start()
        log.info(f"Tray icon for card {self.card} start")

    def stop(self):
        self.tray_icon.visible = False
        self.tray_icon.stop()
        del self.tray_icon
        del self.thread
        log.info(f"Tray icon for card {self.card} stop")

    def refresh(self):
        with pulsectl.Pulse('event-printer') as pulse:
            self.card = pulse.card_info(self.card.index)
        self.tray_icon.menu = self._create_menu(self.card)
        self.tray_icon.icon = self._create_image(self.card.profile_active.name)

    def set_as_default(self):
        with pulsectl.Pulse('event-printer') as pulse:
            source_by_description = next(
                (source for source in pulse.source_list() if source.description == self.description), None)
            if source_by_description:
                pulse.source_default_set(source_by_description)

            sink_by_description = next(
                (source for source in pulse.sink_list() if source.description == self.description), None)
            if sink_by_description:
                pulse.sink_default_set(sink_by_description)

    def __set_profile(self, icon, item):
        profile = item.profile
        log.info(f"set profile {profile.description}")
        with pulsectl.Pulse('event-printer') as pulse:
            pulse.card_profile_set(self.card, profile)
            self.set_as_default()
        self.refresh()


# ----------------------------------------------------------------------------


__card_indicators = {}


def _connect_card(card_index: int):
    global __card_indicators
    with pulsectl.Pulse('event-printer') as pulse:
        card: pulsectl.PulseCardInfo = pulse.card_info(card_index)

        description = card.proplist.get('device.description')
        device_string = card.proplist.get('device.string')

        if len(card.profile_list) <= 2:
            log.warning(f'Ignore card {description} {device_string}')
            return
        card_indicator = HeadphonesIndicator(card)
        __card_indicators[card_index] = card_indicator
        card_indicator.start()
        card_indicator.set_as_default()
        log.info(f'Connected {description} {device_string}')


def _disconnect_card(index):
    global __card_indicators
    __card_indicators[index].stop()
    del __card_indicators[index]


def _change_card(index):
    global __card_indicators

    indicator = __card_indicators.get(index)
    if indicator:
        indicator.refresh()


def _pa_event(event):
    log.debug(f'Receive event {event}')
    if event.t == 'remove' and event.facility == 'card':
        _disconnect_card(event.index)
    elif event.t == 'new' and event.facility == 'card':
        _connect_card(event.index)
    elif event.t == 'change' and event.facility == 'card':
        _change_card(event.index)


def check():
    if not Icon.HAS_MENU:
        log.error(f"{Icon} backedn Menu not supported. Please  pip install -r requirements.txt ")
        sys.exit(2)


def main():
    check()

    with pulsectl.Pulse('event-printer') as pulse:
        card_list = pulse.card_list()
        for card in card_list:
            _connect_card(card.index)
        pulse.event_mask_set('card')
        pulse.event_callback_set(lambda event: _pa_event(event))
        pulse.event_listen()


if __name__ == '__main__':
    main()
