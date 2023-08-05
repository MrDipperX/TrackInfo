from django.db import models
from django.utils.translation import gettext_lazy as _


class PassengerTrack(models.Model):
    number = models.CharField(
        max_length=20, verbose_name=_('Номер вагона'), unique=True
    )
    home_enterprise = models.CharField(
        max_length=50, verbose_name=_("Предприятия приписки"), null=True, blank=True
    )
    wagon_type = models.CharField(
        max_length=50, verbose_name=_("Тип вагона"), null=True, blank=True
    )
    construction_year = models.PositiveSmallIntegerField(
        verbose_name=_("Год постройки"), null=True, blank=True
    )
    building_plant = models.CharField(
        max_length=100, verbose_name=_("Завод постройки"), null=True, blank=True
    )
    state_of_use = models.CharField(
        max_length=100, verbose_name=_("Состояние использования"), null=True, blank=True
    )
    date_to_z = models.DateField(
        verbose_name=_("Дата ТО-З"), null=True, blank=True
    )
    last_dr = models.DateField(
        verbose_name=_("последний ДР"), null=True, blank=True
    )
    last_kr_1 = models.DateField(
        verbose_name=_("последний КР-1"), null=True, blank=True
    )
    last_kr_2 = models.DateField(
        verbose_name=_("последний КР-2"), null=True, blank=True
    )
    last_kvr = models.DateField(
        verbose_name=_("последний КВР"), null=True, blank=True
    )
    assigned_service_life = models.PositiveIntegerField(
        verbose_name=_("Назначенный срок службы"), null=True, blank=True
    )
    service_life = models.PositiveSmallIntegerField(
        verbose_name=_("Срок службы"), null=True, blank=True
    )
    planned_write_of_date = models.DateField(
        verbose_name=_("Плановая дата списания"), null=True, blank=True
    )
    wagon_model = models.CharField(
        max_length=30, verbose_name=_("Модель вагона"), null=True, blank=True
    )
    wagon_tare = models.FloatField(
        verbose_name=_("Тара вагона"), null=True, blank=True
    )
    body_color = models.CharField(
        max_length=50, verbose_name=_("Вид окраски кузова"), null=True, blank=True
    )
    sleeping_place_count = models.PositiveSmallIntegerField(
        verbose_name=_("Количество спальных мест"), null=True, blank=True
    )
    sitting_place_count = models.PositiveSmallIntegerField(
        verbose_name=_("Количество мест для сидения"), null=True, blank=True
    )
    far_and_air_condition_system = models.CharField(
        max_length=100, verbose_name=_("Система вентиляции и кондиционеров"), null=True, blank=True
    )
    generator_type = models.CharField(
        max_length=60, verbose_name=_("Тип генератора"), null=True, blank=True
    )
    generator_drive_design = models.CharField(
        max_length=60, verbose_name=_("Конструкция привода генератора"), null=True, blank=True
    )

    class Meta:
        verbose_name = "Вагон"
        verbose_name_plural = "Вагоны"
        ordering = ('id', )


