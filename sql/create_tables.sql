CREATE DATABASE shine_production_log
	OWNER dbo
	ENCODING 'utf-8';

\c shine_production_log

CREATE TABLE device (
	serial_number		text,
	ieee				varchar(17),
	code_name			text,
	device_type			text,
	hardware_revision	text,
	creation_time		timestamp,
	update_time			timestamp,
	status				smallint
);

CREATE TABLE flashing_log (
	serial_number		text,
	ieee				varchar(17),
	ate_id				smallint,
	command				text,
	firmware_name		text,
	revision			text,
	target_component	text,
	flashing_time		timestamp,
	returned_code		smallint,
	stdout				text,
	stderr				text
);

CREATE TABLE test_log (
	serial_number		text,
	ieee				varchar(17),
	ate_id				smallint,
	test_description	text,
	test_result			text,
	test_time			timestamp
);
