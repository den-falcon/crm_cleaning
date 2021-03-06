from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.forms.models import modelformset_factory
from django.views.generic import DeleteView

from crmapp.forms import BaseStaffAddFormSet, OrderStaffForm
from crmapp.models import StaffOrder, Order
from tgbot.handlers.orders.tg_order_staff import once_staff_add_order, once_staff_remove_order

User = get_user_model()


class OrderStaffCreateView(PermissionRequiredMixin, FormView):
    model = StaffOrder
    formset = BaseStaffAddFormSet
    form_class = OrderStaffForm
    template_name = "staff/create.html"
    permission_required = "crmapp.add_stafforder"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
        orders = Order.objects.filter(Q(work_start__range=[order.work_start, order.work_end]) | Q(
            work_end__range=[order.work_start, order.work_end]))
        staff = []
        for obj in orders:
            staff += obj.cleaners.all()

        exclude_by_time = StaffOrder.objects.filter(staff__in=staff)
        exclude_by_order = StaffOrder.objects.filter(order=order)
        staff_filter = User.objects.filter(is_staff=False, is_active=True, black_list=False,
                                           schedule=order.work_start.isoweekday()).exclude(
            Q(cleaner_orders__in=exclude_by_time or exclude_by_order))

        StaffOrderFormset = modelformset_factory(StaffOrder, form=self.form_class, formset=self.formset, extra=5)
        formset = StaffOrderFormset(prefix="staff")
        for forms in formset:
            forms.fields["staff"].queryset = staff_filter
        context["formset"] = formset
        return context

    def post(self, request, *args, **kwargs):
        StaffOrderFormset = modelformset_factory(StaffOrder, form=self.form_class, formset=self.formset, extra=5)
        formset = StaffOrderFormset(request.POST, prefix="staff")
        if formset.is_valid():
            return self.form_valid(formset)

    def form_valid(self, formset):
        order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
        form = formset.save(commit=False)
        for obj in form:
            obj.order = order
            obj.save()
            once_staff_add_order(obj)
        return redirect("crmapp:order_detail", pk=order.pk)

    def has_permission(self):
        order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
        return self.request.user == order.manager or self.request.user.is_staff


class OrderStaffDeleteView(PermissionRequiredMixin, DeleteView):
    model = StaffOrder
    template_name = 'staff/delete.html'
    context_object_name = 'staff'

    def form_valid(self, form):
        self.object.delete()
        once_staff_remove_order(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('crmapp:order_detail', kwargs={'pk': self.object.order.pk})

    def has_permission(self):
        return self.request.user == self.get_object().order.manager or self.request.user.is_staff


class StaffOrderCreateView(PermissionRequiredMixin, CreateView):
    model = StaffOrder
    template_name = 'service_order/service_order_create.html'
    success_url = reverse_lazy('crmapp:service_order_create')
    form_class = OrderStaffForm
    permission_required = "crmapp.add_stafforder"

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        self.object = form.save(commit=False)
        self.object.order = order
        if order.get_brigadier():
            self.object.is_brigadier = False
        self.object.save()
        once_staff_add_order(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('crmapp:order_detail', kwargs={'pk': self.object.order.pk})

    def has_permission(self):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        return self.request.user == order.manager and super().has_permission() or self.request.user.is_staff


class StaffOrderAddBrigadierView(PermissionRequiredMixin, UpdateView):
    model = StaffOrder
    template_name = 'service_order/service_order_create.html'
    success_url = reverse_lazy('crmapp:service_order_create')
    form_class = OrderStaffForm
    permission_required = "crmapp.add_stafforder"

    def post(self, *args, **kwargs):
        staff = get_object_or_404(StaffOrder, pk=self.kwargs.get('pk'))
        staff.is_brigadier = True
        staff.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('crmapp:order_detail', kwargs={'pk': self.object.order.pk})

    def has_permission(self):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        return self.request.user == order.manager and super().has_permission() or self.request.user.is_staff


class StaffOrderDeleteView(PermissionRequiredMixin, DeleteView):
    model = StaffOrder
    template_name = 'service/service_delete.html'
    success_url = reverse_lazy('crmapp:service_list')
    permission_required = "crmapp.delete_service"
