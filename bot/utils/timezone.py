import re
from datetime import datetime, timedelta, timezone


class TimezoneService:
    """
    just simple service for easier work with datetime and timezone
    """

    @classmethod
    def is_timezone(cls, text: str) -> bool:
        """
        Проверяет, что сообщение может является часовым поясом
        """
        p = r"^[+\-]\d{1,2}$"
        if re.match(p, text):
            if -24 < int(text) < 24:
                return True
        return False

    @classmethod
    def str_to_tz(cls, tz: str) -> timezone:
        """
        Конвертирует строку (формата cls.is_timezone) в объект класса timezone
        """
        return timezone(timedelta(hours=int(tz)))

    @classmethod
    def tz_to_str(cls, tz: timezone) -> str:
        """
        Конвертирует timezone в строку под формат cls.is_timezone
        """
        return str(int(tz.utcoffset(None).total_seconds() // 3600))

    @classmethod
    def convert_to_tz(cls, date: datetime, tz: timezone | str) -> datetime:
        """
        Конвертирует дату под указанный часовой пояс.

        Если есть информация о поясе, то можно просто отобразить в другом часовом поясе.

        Если информации нет, то нужно делать это принудительно

        :param date: Объект класса datetime. Допускается, что tzinfo может не быть
        :param tz: Объект класса timezone, либо строка, которую можно конвертировать в timezone
        :return: Возвращает дату под указанный часовой пояс
        """
        if isinstance(tz, str):
            tz = cls.str_to_tz(tz=tz)
        if date.tzinfo:
            return date.astimezone(tz=tz)
        return date.replace(tzinfo=tz)

    @classmethod
    def valid_date(cls, date: datetime, tz: timezone | str = timezone.utc) -> bool:
        """
        Проверяет, что время напоминания не в прошлом
        """
        return datetime.now(tz=timezone.utc) < cls.convert_to_tz(date, tz)
