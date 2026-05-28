from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('stock', '0002_alter_purchaseorder_manager_to_user'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- 1. Trigger para validar quantity_used > 0 en consultation_supplies
            CREATE TRIGGER IF NOT EXISTS check_consultation_supplies_quantity
            BEFORE INSERT ON consultation_supplies
            FOR EACH ROW
            WHEN NEW.quantity_used <= 0
            BEGIN
                SELECT RAISE(ABORT, 'quantity_used debe ser mayor a 0');
            END;

            -- 2. Trigger para validar quantity_used > 0 en clinical_procedures_supplies
            CREATE TRIGGER IF NOT EXISTS check_clinical_procedures_supplies_quantity
            BEFORE INSERT ON clinical_procedures_supplies
            FOR EACH ROW
            WHEN NEW.quantity_used <= 0
            BEGIN
                SELECT RAISE(ABORT, 'quantity_used debe ser mayor a 0');
            END;

            -- 3. Vista de stock bajo (productos con stock actual <= mínimo)
            DROP VIEW IF EXISTS low_stock_alerts;
            CREATE VIEW low_stock_alerts AS
            SELECT
                s.id AS supply_id,
                s.name AS supply_name,
                sb.id AS batch_id,
                sb.lot_number,
                sb.current_stock,
                s.min_stock AS min_stock_threshold
            FROM supplies s
            JOIN supply_batches sb ON s.id = sb.supply_id
            WHERE sb.current_stock <= s.min_stock;
            """,
            reverse_sql="""
            DROP VIEW IF EXISTS low_stock_alerts;
            DROP TRIGGER IF EXISTS check_consultation_supplies_quantity;
            DROP TRIGGER IF EXISTS check_clinical_procedures_supplies_quantity;
            """
        ),
    ]