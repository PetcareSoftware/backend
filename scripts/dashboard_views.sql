CREATE OR REPLACE VIEW view_operational_dashboard AS
SELECT 
    a.id AS appointment_id,
    p.name AS patient_name,
    u.first_name || ' ' || u.last_name AS veterinarian_name,
    a.status AS appointment_status,
    a.reason AS reason_for_visit,
    a.checked_in_at,
    ts.start_time,
    ts.end_time
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN time_slots ts ON a.slot_id = ts.id
JOIN vet_schedules vs ON ts.schedule_id = vs.id
JOIN veterinarians v ON vs.vet_id = v.user_id
JOIN users u ON v.user_id = u.id;

CREATE OR REPLACE VIEW view_inventory_alerts AS
SELECT 
    s.sku,
    s.name AS supply_name,
    s.category,
    COALESCE(SUM(sb.current_stock), 0) AS total_stock,
    s.min_stock_alert,
    CASE 
        WHEN COALESCE(SUM(sb.current_stock), 0) <= s.min_stock_alert THEN 'CRÍTICO - REABASTECER' 
        ELSE 'NORMAL' 
    END AS stock_status
FROM supplies s
LEFT JOIN supply_batches sb ON s.id = sb.supply_id
GROUP BY s.id, s.sku, s.name, s.category, s.min_stock_alert;


CREATE OR REPLACE VIEW view_clinical_summary AS
SELECT 
    c.id AS consultation_id,
    p.name AS patient_name,
    c.consultation_type,
    c.created_at AS consultation_date,
    d.name AS diagnosis_name,
    cp.procedure_name
FROM consultations c
JOIN medical_records mr ON c.medical_record_id = mr.id
JOIN patients p ON mr.patient_id = p.id
LEFT JOIN consultation_details cd ON c.id = cd.consultation_id
LEFT JOIN diagnoses d ON cd.diagnosis_id = d.id
LEFT JOIN clinical_procedures cp ON c.id = cp.consultation_id;