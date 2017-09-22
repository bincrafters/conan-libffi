#include <stdio.h>
#include <ffi.h>

int main()
{
	ffi_type *atypes[1] = {&ffi_type_uint};
    ffi_cif cif;
    ffi_status status = ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 1, &ffi_type_uint, atypes);
    if (status != FFI_OK)
	{
		printf("Error initializing libffi.\n");
        return -1;
    }

	printf("Successfully initialized libffi.\n");
	return 0;
}
