from django.db import migrations

FORWARD = """
DROP TRIGGER IF EXISTS protect_mother_property_identifier;
CREATE TRIGGER protect_mother_property_identifier
BEFORE UPDATE OF identifier ON properties_motherproperty
FOR EACH ROW
WHEN OLD.identifier <> NEW.identifier
BEGIN
    SELECT RAISE(ABORT, 'mother property identifier is immutable');
END;
"""

REVERSE = """
DROP TRIGGER IF EXISTS protect_mother_property_identifier;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0004_mother_property_dossier"),
    ]
    operations = [
        migrations.RunSQL(sql=FORWARD, reverse_sql=REVERSE),
    ]
