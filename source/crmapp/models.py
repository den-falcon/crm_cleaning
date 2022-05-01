from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _

from crmapp.choice import PaymentChoices, UnitChoices, OrderStatusChoices


class Service(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False, verbose_name=_('Услуга'))
    unit = models.CharField(max_length=350, null=False, blank=False, choices=UnitChoices.choices,
                            verbose_name=_('Единица измерения'), default='square_meter')
    price = models.PositiveIntegerField(verbose_name=_('Цена за единицу'), null=False, blank=False)
    is_extra = models.BooleanField(verbose_name=_('Доп. услуга'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'extra_services'
        verbose_name = _('Дополнительная услуга')
        verbose_name_plural = _('Дополнительные услуги')


class Client(models.Model):
    first_name = models.CharField(verbose_name=_('Имя'), max_length=75, blank=False, null=False)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=75, blank=False, null=False)
    phone = PhoneNumberField(unique=True, region="KG", max_length=15, verbose_name=_('Номер телефона'))

    @property
    def get_absolute_url(self):
        return reverse('crmapp:client_index')

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.phone}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'client'
        verbose_name = _('Клиент')
        verbose_name_plural = _('Клиенты')


class ForemanReport(models.Model):
    # Таблица для отчёта бригадира имеет связь FK с таблицей Order
    order = models.ForeignKey('crmapp.Order', on_delete=models.PROTECT, null=False, blank=False,
                              related_name='foreman_order_report', verbose_name=_('Заказ'))
    expenses = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Расходы'))
    start_at = models.DateTimeField(verbose_name=_('Дата и время начала работы'))
    end_at = models.DateTimeField(verbose_name=_('Дата и время окончания работы'))
    photo_before = models.ManyToManyField('crmapp.ForemanPhoto',
                                          related_name='foreman_photo_before', verbose_name=_('Фото до начала работ'))
    photo_after = models.ManyToManyField('crmapp.ForemanPhoto',
                                         related_name='foreman_photo_after',
                                         verbose_name=_('Фото после окончания работ'))


class ForemanPhoto(models.Model):
    # Таблица для хранения фотографий, имеет связь m2m с таблицей ForemanReport
    image = models.ImageField(upload_to='photo_obj', verbose_name=_('Фото'))


class ForemanOrderUpdate(models.Model):
    # Таблица для редактирования услуг и доп услуг в заказе для бригадира, имеет связь FK с таблицей Order
    order = models.ForeignKey('crmapp.Order', on_delete=models.PROTECT, null=False, blank=False,
                              related_name='foreman_order_update', verbose_name=_('Заказ'))
    service = models.ManyToManyField('crmapp.ServiceOrder', related_name='foreman_service',
                                     verbose_name=_('Услуга'))
    description = models.TextField(max_length=500, blank=True, null=True, verbose_name=_('Причина внесения изменений'))

    class Meta:
        db_table = 'foreman_order_update'
        verbose_name = _('Корректировка бригадира')
        verbose_name_plural = _('Корректировки бригадиров')

class StaffOrder(models.Model):
    order = models.ForeignKey('crmapp.Order', related_name='order_cliners', verbose_name=_('Заказ'), null=False,
                              blank=False, on_delete=models.PROTECT)
    staff = models.ForeignKey(get_user_model(), related_name='cliner_orders', verbose_name=_('Клинер'),
                              null=False, blank=False, on_delete=models.PROTECT)
    is_brigadier = models.BooleanField(verbose_name=_('Бригадир'), default=False)
    is_accept = models.BooleanField(null=True, blank=True, default=False, verbose_name=_('Принял заказ'))
    in_place = models.DateTimeField(null=True, blank=True, verbose_name=_('Время прибытия на заказ'))


class Order(models.Model):  # Таблица самого заказа
    # Поле для сортировки незавершённых работ
    status = models.CharField(max_length=50, default='new', verbose_name=_('Статус заказа'),
                              choices=OrderStatusChoices.choices, null=False, blank=False)
    object_type = models.ForeignKey('crmapp.ObjectType', on_delete=models.PROTECT, related_name='orders',
                                    verbose_name=_('Тип объекта'), null=True, blank=True)

    # Поля связанные со временем
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата и время создания заказа'))
    work_start = models.DateTimeField(verbose_name=_('Дата и время выполнения уборки'))
    cleaning_time = models.TimeField(verbose_name=_('Время выполнения работ'))

    # Информация о клиенте
    client_info = models.ForeignKey('crmapp.Client', on_delete=models.PROTECT, related_name='order_client',
                                    verbose_name=_('Информация клиента'))
    address = models.CharField(max_length=256, null=False, blank=False, verbose_name=_('Адрес'))

    # Уборки
    services = models.ManyToManyField('crmapp.Service', related_name='orders',
                                      verbose_name=_('Услуга'), through='crmapp.ServiceOrder',
                                      through_fields=('order', 'service'))

    # Поля для Staff
    manager = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='manager_order',
                                verbose_name=_('Менеджер'))
    cleaners = models.ManyToManyField(get_user_model(), related_name='orders', verbose_name=_('Клинер'),
                                      through='crmapp.StaffOrder',
                                      through_fields=('order', 'staff'))

    review = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
                                         verbose_name=_('Отзыв'))
    # Финансовая часть
    payment_type = models.CharField(max_length=25, null=False, blank=False, default='cash',
                                    choices=PaymentChoices.choices,
                                    verbose_name=_('Вид оплаты'))  # вид оплаты
    total_cost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Общая сумма заказа'))


class FineCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Категория'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'fine_category'
        verbose_name = _('Категория для штрафа')
        verbose_name_plural = _('Категории для штрафа')


class Fine(models.Model):
    category = models.ForeignKey('crmapp.FineCategory', on_delete=models.PROTECT, null=True, blank=True,
                                 related_name='fines', verbose_name=_('Категория'))
    fine = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('Штраф'))
    criteria = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Критерий'))
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Сумма штрафа'))
    description = models.TextField(max_length=500, blank=True, null=True, verbose_name=_('Пояснение'))

    def __str__(self):
        return f"{self.fine} - {self.value}"

    class Meta:
        db_table = 'fine'
        verbose_name = _('Штраф')
        verbose_name_plural = _('Штрафы')


class Bonus(models.Model):
    bonus = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('Бонус'))
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Сумма бонуса'))

    def __str__(self):
        return f"{self.bonus} - {self.value}"

    class Meta:
        db_table = 'bonus'
        verbose_name = _('Бонус')
        verbose_name_plural = _('Бонусы')


class Inventory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Инвентарь'), null=False, blank=False)
    description = models.TextField(max_length=1000, verbose_name=_('Описание'), null=True, blank=True)

    @property
    def get_absolute_url(self):
        return reverse('crmapp:inventory_index')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "inventory"
        verbose_name = _("Инвентарь")
        verbose_name_plural = _("Инвентари")


class Cleanser(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Моющее средство'), null=False, blank=False)
    description = models.TextField(max_length=1000, verbose_name=_('Описание товара'), null=True, blank=True)

    @property
    def get_absolute_url(self):
        return reverse('crmapp:cleanser_index')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "cleanser"
        verbose_name = _("Моющее средство")
        verbose_name_plural = _("Моющие средства")


class ServiceOrder(models.Model):
    order = models.ForeignKey('crmapp.Order', related_name='order_services', verbose_name=_('Заказ'), null=False,
                              blank=False, on_delete=models.PROTECT)
    service = models.ForeignKey('crmapp.Service', related_name='service_orders', verbose_name=_('Услуга'),
                                null=False, blank=False, on_delete=models.PROTECT)
    amount = models.IntegerField(verbose_name=_('Объем работы'), null=False, blank=False)
    rate = models.DecimalField(default=1, null=False, blank=False, verbose_name=_('Коэффицент сложности'),
                               max_digits=2, decimal_places=1,
                               validators=[MinValueValidator(1.0), MaxValueValidator(3.0)])
    total = models.PositiveIntegerField(null=False, blank=False, verbose_name=_('Стоимость услуги'))

    def __str__(self):
        return f"{self.service}: {self.total}"

    class Meta:
        db_table = "service_order"
        verbose_name = _("Услуга заказа")
        verbose_name_plural = _("Услуги заказа")


class InventoryInOrder(models.Model):
    order = models.ForeignKey('crmapp.Order', related_name='order_inventories', verbose_name=_('Заказ'),
                              null=True, blank=True, on_delete=models.PROTECT)
    inventory = models.ForeignKey('crmapp.Inventory', related_name='inventories_order',
                                  verbose_name=_('Инвентарь'), null=True, blank=True, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(verbose_name=_('Количество'), null=True, blank=True)

    def __str__(self):
        return f'{self.inventory}:{self.amount}'

    class Meta:
        db_table = 'inventory_in_order'
        verbose_name = _('Инвентарь заказа')
        verbose_name_plural = _('Инвентари заказа')


class CleanserInOrder(models.Model):
    order = models.ForeignKey('crmapp.Order', related_name='order_cleanser', verbose_name=_('Заказ'),
                              null=True, blank=True, on_delete=models.PROTECT)
    cleanser = models.ForeignKey('crmapp.Cleanser', related_name='cleansers_order',
                                 verbose_name=_('Моющее средство'), null=True, blank=True, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(verbose_name=_('Количество'), null=True, blank=True)

    def __str__(self):
        return f'{self.cleanser}:{self.amount}'

    class Meta:
        db_table = 'cleanser_in_order'
        verbose_name = _('Моющее средство в заказе')
        verbose_name_plural = _('Моющие средства в заказе')


class ObjectType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Наименование'), null=False, blank=False)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'object_types'
        verbose_name = _('Тип объекта')
        verbose_name_plural = _('Типы объекта')
