from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import SchoolFeeStructure # Import the fee structure model

# Signal to capture when components are added/removed from a structure
@receiver(m2m_changed, sender=SchoolFeeStructure.components.through)
def update_total_on_m2m_change(sender, instance, action, **kwargs):
    """
    Triggers recalculation when a component is added, removed, or cleared 
    from a SchoolFeeStructure instance.
    """
    # Only act on actions that change the composition of the total
    if action in ['post_add', 'post_remove', 'post_clear']:
        # 'instance' here is the SchoolFeeStructure object
        instance.calculate_total_amount_required()