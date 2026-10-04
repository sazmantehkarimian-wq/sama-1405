from django.db.models.signals import post_save
from django.dispatch import receiver

from domains.auctionflow.models import AuctionLotProfile
from domains.contracts.models import ContractCirculation


@receiver(post_save, sender=ContractCirculation)
def sync_award_contract(sender, instance, **kwargs):
    """Keep the winning auction lot linked to the official contract after final conversion."""
    if not instance.official_contract_id:
        return
    try:
        profile=instance.auction_award
    except AuctionLotProfile.DoesNotExist:
        return
    changed=[]
    if profile.official_contract_id != instance.official_contract_id:
        profile.official_contract=instance.official_contract
        changed.append('official_contract')
    if profile.result_state != AuctionLotProfile.ResultState.CONTRACTED:
        profile.result_state=AuctionLotProfile.ResultState.CONTRACTED
        changed.append('result_state')
    if changed:
        changed.append('updated_at')
        profile.save(update_fields=changed)
