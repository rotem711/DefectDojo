from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dojo', '0007_note_additions'),
    ]

    operations = [
        migrations.AddField(
            model_name='finding',
            name='Mitigated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='child_rule',
            name='match_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('Mitigated', 'Mitigated'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence')], max_length=200),
        ),
        migrations.AlterField(
            model_name='finding',
            name='mitigated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='applied_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('Mitigated', 'Mitigated'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence')], max_length=200),
        ),
        migrations.AlterField(
            model_name='rule',
            name='match_field',
            field=models.CharField(choices=[('id', 'id'), ('title', 'title'), ('date', 'date'), ('cwe', 'cwe'), ('cve', 'cve'), ('url', 'url'), ('severity', 'severity'), ('description', 'description'), ('mitigation', 'mitigation'), ('impact', 'impact'), ('steps_to_reproduce', 'steps_to_reproduce'), ('severity_justification', 'severity_justification'), ('references', 'references'), ('test', 'test'), ('is_template', 'is_template'), ('active', 'active'), ('verified', 'verified'), ('false_p', 'false_p'), ('duplicate', 'duplicate'), ('duplicate_finding', 'duplicate_finding'), ('out_of_scope', 'out_of_scope'), ('under_review', 'under_review'), ('review_requested_by', 'review_requested_by'), ('Mitigated', 'Mitigated'), ('under_defect_review', 'under_defect_review'), ('defect_review_requested_by', 'defect_review_requested_by'), ('thread_id', 'thread_id'), ('mitigated', 'mitigated'), ('mitigated_by', 'mitigated_by'), ('reporter', 'reporter'), ('numerical_severity', 'numerical_severity'), ('last_reviewed', 'last_reviewed'), ('last_reviewed_by', 'last_reviewed_by'), ('line_number', 'line_number'), ('sourcefilepath', 'sourcefilepath'), ('sourcefile', 'sourcefile'), ('param', 'param'), ('payload', 'payload'), ('hash_code', 'hash_code'), ('line', 'line'), ('file_path', 'file_path'), ('static_finding', 'static_finding'), ('dynamic_finding', 'dynamic_finding'), ('created', 'created'), ('scanner_confidence', 'scanner_confidence')], max_length=200),
        ),
    ]
