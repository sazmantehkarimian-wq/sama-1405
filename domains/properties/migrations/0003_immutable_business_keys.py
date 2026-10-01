from django.db import migrations

FORWARD = """
CREATE TRIGGER IF NOT EXISTS protect_commercial_space_code
BEFORE UPDATE OF code ON properties_commercialspace
FOR EACH ROW
WHEN OLD.code <> NEW.code
BEGIN
    SELECT RAISE(ABORT, 'commercial space code is immutable');
END;

CREATE TRIGGER IF NOT EXISTS protect_mother_property_identifier
BEFORE UPDATE OF identifier ON properties_motherproperty
FOR EACH ROW
WHEN OLD.identifier <> NEW.identifier
BEGIN
    SELECT RAISE(ABORT, 'mother property identifier is immutable');
END;
"""

REVERSE = """
DROP TRIGGER IF EXISTS protect_commercial_space_code;
DROP TRIGGER IF EXISTS protect_mother_property_identifier;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0002_zero_data_foundation"),
    ]
    operations = [
        migrations.RunSQL(sql=FORWARD, reverse_sql=REVERSE),
    ]
