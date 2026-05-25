import itertools
import os
import subprocess
import datetime
import shutil

# Flag descriptions dictionary
FLAG_DESCRIPTIONS = {
    "/Oa": "ignore aliasing",
    "/Od": "disable optimizations",
    "/Oi": "enable intrinsic functions",
    "/Ol": "enable loop optimizations",
    "/On": "disable 'unsafe' optimizations",
    "/Op": "enable precision optimizations",
    "/Or": "disable in_line return",
    "/Os": "optimize for space",
    "/Ot": "optimize for speed (default)",
    "/Gs": "no stack checking",
    "/Zi": "add debug info",
    "": "no flags"
}

# Define all compiler flags to test
FLAGS = list(FLAG_DESCRIPTIONS.keys())

# --- Filtering Logic ---

# 1. Define mutually exclusive groups. A combination is invalid if it contains
#    more than one flag from any of these sets.
exclusive_groups = [
    # A file can only have one primary optimization goal.
    # /Zi and /Od both disable optimizations, so they are in this group.
    {'/Od', '/Os', '/Ot'} #, '/Zi'}
]

# 2. Define dependency rules. The key is the required flag, 
#    the value is a set of flags that depend on it.
#    For simplicity here, we define that fine-grained '/O' flags
#    are meaningless with /Od or /Zi.
_dependent_flags = {
    '/Od': {'/Oa', '/Oi', '/Ol', '/On', '/Op', '/Or', '/Os', '/Ot'},
    '/Zi': {'/Oa', '/Oi', '/Ol', '/On', '/Op', '/Or', '/Os', '/Ot'}
}

# Generate all possible combinations first
all_combinations_raw = []
for r in range(len(FLAGS) + 1):
    for combo in itertools.combinations(FLAGS, r):
        # Create a set for efficient checking
        all_combinations_raw.append(set(combo))

print(f"Total theoretical combinations: {len(all_combinations_raw)}")

# Filter the combinations based on the rules
filtered_combinations = []
for combo_set in all_combinations_raw:
    is_valid = True
    
    # Rule 1: Check for mutual exclusivity
    for group in exclusive_groups:
        if len(combo_set.intersection(group)) > 1:
            is_valid = False
            break
    if not is_valid:
        continue
        
    # Rule 2: Check for dependencies
    #for required, dependents in dependent_flags.items():
    #    if required in combo_set and combo_set.intersection(dependents):
    #        is_valid = False
    #        break
    if not is_valid:
        continue

    # If all checks pass, add it to the list
    filtered_combinations.append(" ".join(sorted(list(combo_set)))) # Sort for consistent naming

# --- End of Filtering Logic ---


# Print total number of combinations
print(f"Filtered combinations to test: {len(filtered_combinations)}")

# Path to dosbuild.sh script
DOSBUILD_PATH = "mzretools/tools/dosbuild.sh"

# Create summary file with timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
summary_file = f"COMPILER/compiler_flags_summary_{timestamp}.txt"
with open(summary_file, "w") as summary:
    summary.write(f"Compiler Flag Test Summary - {timestamp}\n")
    summary.write("="*50 + "\n\n")
    summary.write(f"Total theoretical combinations: {len(all_combinations_raw)}\n")
    summary.write(f"Filtered combinations tested: {len(filtered_combinations)}\n\n")

total_combinations = len(filtered_combinations)
processed = 0

# Compile each valid combination
for i, combo in enumerate(filtered_combinations):
    processed += 1
    remaining = total_combinations - processed
    
    # Create safe filename from flags
    safe_name = combo.replace("/", "").replace(" ", "_") or "default"
    cod_file = f"COMPILER/output_{safe_name}.COD"
    
    # Skip if COD file already exists
    if os.path.exists(cod_file):
        print(f"[{processed}/{total_combinations}, Remaining: {remaining}] Skipping (already exists): {cod_file}")
        continue  # Skip to next combination
        
    try:
        if os.path.exists("COMPILER/TESTFLAG.COD"):
            os.unlink("COMPILER/TESTFLAG.COD")
    except Exception:
        pass

    # Build command
    # Note: Added /Gs to all builds as it's almost always used and independent
    build_flags = "/Fc /c " + combo + " /Gs /Id:\\f15-se2 /Id:\\f15-se2\\src"
    cmd = [DOSBUILD_PATH, "cc", "msc510", "-i", "COMPILER/testflag.c", "-o", "COMPILER/RESULT.TXT", "-f", build_flags]
    
    print(f"[{processed}/{total_combinations}, Remaining: {remaining}] Compiling with flags: {combo or 'none'}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if the COD file was created
    if not os.path.exists("COMPILER/TESTFLAG.COD"):
        print(f"  FAILED to generate COD file. Compiler output:\n{result.stderr}")
        continue

    print(f"  Success: {cod_file}")
    
    # Copy the generated COD file to our named file
    shutil.copyfile("COMPILER/TESTFLAG.COD", cod_file)
    
    # Add to summary
    with open(summary_file, "a") as summary:
        summary.write(f"\n\n=== Flags: {combo or 'none'} ===\n")
        
        # Add flag descriptions
        flags_in_combo = combo.split()
        if flags_in_combo:
            for flag in flags_in_combo:
                description = FLAG_DESCRIPTIONS.get(flag, "Unknown flag")
                summary.write(f"  {flag}: {description}\n")
        else:
            summary.write("  No flags (default optimization)\n")
            
        summary.write(f"Output file: {cod_file}\n")
        summary.write("-"*50 + "\n")
        
        # Read and append the COD file
        try:
            with open(cod_file, "r") as f:
                summary.write(f.read())
        except Exception as e:
            summary.write(f"Error reading {cod_file}: {str(e)}")

print("\nAll compilations completed!")
print(f"Summary file created: {summary_file}")
