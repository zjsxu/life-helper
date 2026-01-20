# GitHub Issue Testing Guide

## Overview

This guide walks you through testing the GitHub Interface integration with a real GitHub Issue. This is the final validation step before considering the deployment complete.

## Prerequisites

Before testing, ensure:
- ✅ All code changes are committed
- ✅ The `v0.3-stable` tag exists
- ✅ All changes are pushed to GitHub (including the tag)
- ✅ The repository is accessible on GitHub

## Step 1: Push Changes to GitHub

If you haven't already pushed your changes:

```bash
# Push main branch
git push origin main

# Push the v0.3-stable tag
git push origin v0.3-stable
```

## Step 2: Create a Test Issue

1. **Navigate to your repository on GitHub**
   - Go to: `https://github.com/<your-username>/<your-repo>`

2. **Click "Issues" tab**

3. **Click "New Issue" button**

4. **Select "Life Check-in" template**
   - You should see the structured form with required fields

5. **Fill in the test data** (NORMAL state scenario):
   ```
   Non-movable deadlines (next 14 days): 1
   Active high-load domains: 1
   Energy (1–5, comma-separated): 4,4,5
   Tasks / commitments: (leave empty or add test tasks)
   ```

6. **Click "Submit new issue"**

## Step 3: Verify Workflow Triggers

1. **Go to the "Actions" tab** in your repository

2. **Look for a workflow run** named "Life Orchestrator"
   - It should appear within a few seconds of creating the Issue
   - Status should show as "Running" or "Completed"

3. **Click on the workflow run** to see details

4. **Verify the steps**:
   - ✅ Checkout repository
   - ✅ Set up Python 3.13
   - ✅ Install dependencies
   - ✅ Run evaluation
   - ✅ Post comment

5. **Check for errors**:
   - If any step fails, click on it to see the error details
   - Common issues:
     - Dependency installation failures
     - Python import errors
     - Script execution errors

## Step 4: Verify Comment Posted

1. **Return to the Issue you created**

2. **Look for a comment from "github-actions[bot]"**
   - Should appear within 30-60 seconds

3. **Verify the comment format**:
   ```
   ```
   === Personal Decision-Support System ===
   
   Current State: NORMAL
   Reason: ...
   
   Planning Permission: ALLOWED
   Execution Permission: DENIED
   
   Authority Mode: NORMAL
   
   Recovery Status: Ready
   ...
   ```
   ```

4. **Check the content**:
   - ✅ State should be "NORMAL" (based on test inputs)
   - ✅ Planning Permission should be "ALLOWED"
   - ✅ Execution Permission should be "DENIED"
   - ✅ Authority Mode should be "NORMAL"
   - ✅ Output should be wrapped in markdown code block

## Step 5: Test OVERLOADED State

Create another test Issue with OVERLOADED state inputs:

```
Non-movable deadlines (next 14 days): 4
Active high-load domains: 3
Energy (1–5, comma-separated): 2,2,2
Tasks / commitments: (optional)
```

**Expected output**:
- State: OVERLOADED
- Planning Permission: DENIED
- Authority Mode: CONTAINMENT
- Active downgrade rules listed

## Step 6: Test Error Handling

Create a test Issue with invalid data:

```
Non-movable deadlines (next 14 days): abc
Active high-load domains: 2
Energy (1–5, comma-separated): 3,3,3
```

**Expected output**:
- Error message explaining the invalid input
- Clear guidance on how to fix it
- No system crash or workflow failure

## Step 7: Test Issue Editing

1. **Edit one of your test Issues**
   - Change the energy scores
   - Click "Update comment"

2. **Verify workflow triggers again**
   - Check Actions tab for new workflow run

3. **Verify new comment posted**
   - Should reflect the updated values

## Verification Checklist

After completing all tests, verify:

- [ ] Issue template appears in New Issue menu
- [ ] Template has all required fields (deadlines, domains, energy)
- [ ] Template has optional tasks field
- [ ] "life-checkin" label applied automatically
- [ ] Title prefix "[Life] Check-in" applied automatically
- [ ] Workflow triggers on Issue creation
- [ ] Workflow triggers on Issue editing
- [ ] Workflow does NOT trigger on Issues without "life-checkin" label
- [ ] Python 3.13 environment set up correctly
- [ ] Dependencies install successfully
- [ ] Glue script executes without errors
- [ ] Comment posted by github-actions bot
- [ ] Comment format matches CLI output
- [ ] NORMAL state produces correct output
- [ ] OVERLOADED state produces correct output
- [ ] Invalid inputs produce clear error messages
- [ ] Output is deterministic (same inputs = same output)
- [ ] No repository modifications occur
- [ ] Frozen components remain unchanged

## Troubleshooting

### Workflow Doesn't Trigger

**Possible causes**:
- Issue doesn't have "life-checkin" label
- Workflow file not pushed to GitHub
- Workflow file has syntax errors

**Solutions**:
- Manually add "life-checkin" label to Issue
- Verify `.github/workflows/life_orchestrator.yml` exists on GitHub
- Check Actions tab for workflow syntax errors

### Comment Not Posted

**Possible causes**:
- Workflow permissions insufficient
- Script execution failed
- GitHub API rate limit

**Solutions**:
- Check workflow permissions in YAML file
- Review workflow logs for errors
- Wait a few minutes and try again

### Script Execution Errors

**Possible causes**:
- Import errors (missing dependencies)
- Parsing errors (unexpected Issue format)
- Configuration errors (config.yaml not found)

**Solutions**:
- Check "Install dependencies" step logs
- Verify requirements.txt includes all dependencies
- Ensure config.yaml is in repository root

### Wrong Output Format

**Possible causes**:
- Glue script not using format_output()
- Output not wrapped in code block
- Encoding issues

**Solutions**:
- Verify glue script imports format_output from main.py
- Check comment posting step in workflow
- Review workflow logs for encoding errors

## Success Criteria

The test is successful when:

1. ✅ Issue template works correctly
2. ✅ Workflow triggers on Issue events
3. ✅ All workflow steps complete successfully
4. ✅ Comment posted with correct format
5. ✅ Output matches CLI behavior
6. ✅ Error handling works correctly
7. ✅ No repository modifications occur
8. ✅ Frozen components remain unchanged

## Next Steps After Successful Testing

Once all tests pass:

1. **Document the test results**
   - Take screenshots of successful workflow runs
   - Save example Issue/comment pairs
   - Note any issues encountered and how they were resolved

2. **Update the deployment checklist**
   - Mark task 18.3 as complete
   - Add test results to documentation

3. **Consider the system production-ready**
   - The GitHub Interface is fully functional
   - Users can interact with the system via Issues
   - All safety guarantees are preserved

## Notes

- The first workflow run may take longer due to dependency installation
- Subsequent runs should be faster (dependencies cached)
- You can create multiple test Issues to verify consistency
- Test Issues can be closed after verification
- The system is read-only - no repository modifications will occur

## Example Test Issues

### Test 1: NORMAL State
```
Title: [Life] Check-in - Test NORMAL
Labels: life-checkin

Non-movable deadlines (next 14 days): 1
Active high-load domains: 1
Energy (1–5, comma-separated): 4,4,5
Tasks / commitments: Review documentation
```

### Test 2: STRESSED State
```
Title: [Life] Check-in - Test STRESSED
Labels: life-checkin

Non-movable deadlines (next 14 days): 3
Active high-load domains: 2
Energy (1–5, comma-separated): 3,3,3
Tasks / commitments: Multiple deadlines approaching
```

### Test 3: OVERLOADED State
```
Title: [Life] Check-in - Test OVERLOADED
Labels: life-checkin

Non-movable deadlines (next 14 days): 4
Active high-load domains: 3
Energy (1–5, comma-separated): 2,2,2
Tasks / commitments: Too many commitments
```

### Test 4: Invalid Input
```
Title: [Life] Check-in - Test Error Handling
Labels: life-checkin

Non-movable deadlines (next 14 days): not-a-number
Active high-load domains: 2
Energy (1–5, comma-separated): 3,3,3
```

## Manual Testing Checklist

Use this checklist while testing:

```
[ ] Created test Issue with NORMAL state inputs
[ ] Verified workflow triggered
[ ] Verified comment posted
[ ] Verified output format correct
[ ] Verified state determination correct
[ ] Verified authority enforcement correct

[ ] Created test Issue with OVERLOADED state inputs
[ ] Verified containment mode activated
[ ] Verified planning denied
[ ] Verified downgrade rules listed

[ ] Created test Issue with invalid inputs
[ ] Verified error message clear
[ ] Verified error handling graceful
[ ] Verified no system crash

[ ] Edited existing Issue
[ ] Verified workflow triggered on edit
[ ] Verified new comment posted
[ ] Verified output reflects changes

[ ] Verified no repository modifications
[ ] Verified frozen components unchanged
[ ] Verified workflow permissions correct
```

---

**Status**: Ready for manual testing

**Next Action**: Follow this guide to test with real GitHub Issues
