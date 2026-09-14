#ifndef AMIGUARD_FILE_SIGNATURES_H
#define AMIGUARD_FILE_SIGNATURES_H

struct amiguard_file_signature {
    const char *name;
    unsigned long offset;
    unsigned int length;
    const unsigned char *pattern;
    const unsigned char *mask;
    int test_only;
};

struct amiguard_file_signature_match {
    int matched;
    int test_only;
    const char *name;
};

const struct amiguard_file_signature *amiguard_file_signatures(unsigned long *count);
unsigned long amiguard_file_signature_count(void);

/*
 * Runtime signature database support.
 *
 * A database is parsed and validated completely before it replaces the active
 * runtime table.  On any failure the previously active table is preserved.
 * Built-in generated signatures remain the fallback and can be restored with
 * amiguard_file_signature_use_builtin().
 */
int amiguard_file_signature_load_database(
    const char *path,
    char *detail,
    unsigned long detail_size
);
void amiguard_file_signature_use_builtin(void);
int amiguard_file_signature_database_active(void);
const char *amiguard_file_signature_database_source(void);

struct amiguard_file_signature_match amiguard_match_file_signature(
    const unsigned char *data,
    unsigned long size
);

#endif
