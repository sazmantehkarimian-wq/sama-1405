from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from domains.auctionflow.models import AuctionDocumentInstance, AuctionLotProfile
from domains.contracts.models import ContractCirculation

REFERENCE_HASHES={
    ('CONDITIONS','COMMERCIAL'):'925d4e36d5d63c81645e2c67c1a356b7e7fc89e167d6f98ff55e09d19a369131',
    ('CONDITIONS','CAFE'):'0926059b336ba39e76fa0186a67085d62bcd09f01be311c724a527c8267b2381',
    ('CONDITIONS','SPORT'):'6b2dc335a16767eabcfcc91c30dd5417efd4dbf5170e5d744982000e904f4553',
    ('PRICE_FORM',''):'dff758d7549f1effc59733b040d91da7eb67032e9c22d4f16e1bf9833b4c281f',
    ('OPENING_MINUTES',''):'2d698909a182c249a218bd75af2e770d5be91156d7d6c84f3715860e3b77b566',
    ('EXPERT_NOTICE',''):'13adc308ff902dda352fe59ad90490557744e7ff646ca606db70612b77486860',
    ('SAMPLE_CONTRACT','COMMERCIAL'):'811ac0e9bc853dae9c7d172493c038dc9007a61a08f495ebf19892de06f66a9b',
    ('SAMPLE_CONTRACT','CAFE'):'5d4ba166e3cda354702e1782dc19a93c9c8d22806582c2fc982e429e5a424690',
    ('SAMPLE_CONTRACT','SPORT'):'15b61ebf77d4f123647b326d7cd117ec4176c95a8dd0f2332f89846d8b47fc2c',
    ('ENVELOPE_A',''):'dff758d7549f1effc59733b040d91da7eb67032e9c22d4f16e1bf9833b4c281f',
    ('ENVELOPE_B',''):'dff758d7549f1effc59733b040d91da7eb67032e9c22d4f16e1bf9833b4c281f',
    ('ENVELOPE_C',''):'dff758d7549f1effc59733b040d91da7eb67032e9c22d4f16e1bf9833b4c281f',
}


@receiver(pre_save, sender=AuctionDocumentInstance)
def pin_reference_hash(sender, instance, **kwargs):
    value=REFERENCE_HASHES.get((instance.document_type,instance.template_family)) or REFERENCE_HASHES.get((instance.document_type,''))
    if value:
        instance.source_sha256=value


@receiver(post_save, sender=ContractCirculation)
def sync_award_contract(sender, instance, **kwargs):
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
