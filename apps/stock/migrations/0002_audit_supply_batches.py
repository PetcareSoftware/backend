from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'), 
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS audit_supply_batches (
                audit_id SERIAL PRIMARY KEY,
                batch_id UUID,
                action VARCHAR(10),
                old_data JSONB,
                new_data JSONB,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                changed_by VARCHAR(255) DEFAULT CURRENT_USER
            );

            CREATE OR REPLACE FUNCTION audit_supply_batches_changes()
            RETURNS TRIGGER AS $$
            BEGIN
                IF (TG_OP = 'UPDATE') THEN
                    INSERT INTO audit_supply_batches(batch_id, action, old_data, new_data)
                    VALUES (OLD.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
                    RETURN NEW;
                ELSIF (TG_OP = 'DELETE') THEN
                    INSERT INTO audit_supply_batches(batch_id, action, old_data, new_data)
                    VALUES (OLD.id, 'DELETE', row_to_json(OLD), NULL);
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_audit_supply_batches
            AFTER UPDATE OR DELETE ON supply_batches
            FOR EACH ROW
            EXECUTE FUNCTION audit_supply_batches_changes();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trg_audit_supply_batches ON supply_batches;
            DROP FUNCTION IF EXISTS audit_supply_batches_changes();
            DROP TABLE IF EXISTS audit_supply_batches;
            """
        )
    ]