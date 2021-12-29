CREATE TABLE reminder(
        reminder_id INTEGER PRIMARY KEY, /* unique id for a reminder event */
        reminder_script_nm TEXT,/* name of script inserting the data */
        reminder_script_url TEXT, /* full path of reminder script inserting data */
        reminder_gmts TEXT, /* reminder event time stamp in gmts */
        reminder_ts TEXT, /* reminder event time stamp in AZ time zone */
        reminder_day_of_wk TEXT, /* reminder event day of week */
        reminder_date TEXT, /* reminder event date */
        reminder_type TEXT, /* reminder type ['potty','feeding'] */
        helper_id INTEGER, /* name of family member assigned to take action on this reminder */
        reminder_audio_file_nm TEXT, /* audio file name selected for this reminder */
        reminder_audio_file_url TEXT, /* full path of audio file name selected for this reminder */
        FOREIGN KEY (helper_id)
                REFERENCES helper (helper_id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
);
