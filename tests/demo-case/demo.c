#include <string.h>

void copy_device_name(char *external_name)
{
    char device_name[8];
    strcpy(device_name, external_name); /* CR-DEMO-001 */
}
