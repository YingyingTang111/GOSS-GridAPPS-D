
* System dependence
$if %system.filesys% == UNIX $set sep '/'
$if not %system.filesys% == UNIX $set sep '\'

*define the path and name of case to be used
$set case "case118_FINAL.gdx"
*$set case "case118_updated_FINAL.gdx"

* Printout options
$ifthen %verbose% == 0
* Turn off print options
$offlisting
option limrow=0, limcol=0
$endif

$set savesol 0
* Define filepath, name and extension.
$setnames "%gams.i%" filepath filename fileextension
* Define input case

$if not set case $abort "Model aborted. Please provide input case"
$setnames "%case%" casepath casename caseextension

*$set obj "pwl"

* Default: timeperiod = 1
$if not set timeperiod $set timeperiod "1"
* Default: allon=0
$if not set allon $set allon 0
* Default: Quadratic objective function
$if not set obj $set obj "v_dev"
* Default: Ignore D-curve constraints
$if not set qlim $set qlim 0
* Default: elastic demand bidding does not apply here
$set demandbids 0
* Default: Use provided line limits (as opposed to uwcalc)
$if not set linelimits $set linelimits "given"
* Default: Use provided generator lower limit
$if not set genPmin $set genPmin "0"
* Default: Save solution option turned off
$if not set savesol $set savesol 0

$set condensed 'no'
