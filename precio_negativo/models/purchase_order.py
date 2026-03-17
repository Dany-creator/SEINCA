from odoo import models, api
from odoo.exceptions import ValidationError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _skip_zero_validation_for_alternative_creation(self):
        """Skip zero checks only while an alternative PO is being created."""
        return bool(self.env.context.get('origin_po_id'))

    @api.constrains('price_unit', 'product_qty')
    def _check_negative_values(self):
        for line in self:
            if line.price_unit < 0:
                raise ValidationError("No se permiten precios unitarios negativos en las órdenes de compra.")
            if line.product_qty < 0:
                raise ValidationError("No se permiten cantidades negativas en las órdenes de compra.")
            if line.price_unit == 0:
                if not line._skip_zero_validation_for_alternative_creation() and line.order_id.state not in ['draft', 'sent']:
                    raise ValidationError("No se permiten precios unitarios en 0 en las órdenes de compra.")
            if line.product_qty == 0 and not line._skip_zero_validation_for_alternative_creation():
                raise ValidationError("No se permiten cantidades en 0 en las órdenes de compra.")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for order in self:
            zero_lines = order.order_line.filtered(lambda l: l.price_unit == 0 or l.product_qty == 0)
            if zero_lines:
                raise ValidationError("No se permiten precios unitarios o cantidades en 0 al confirmar la orden de compra.")
        return super().button_confirm()
