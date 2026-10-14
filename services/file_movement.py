def current_holder(space):
 return space.file_movements.filter(returned_at__isnull=True).order_by('-handover_at').first()
