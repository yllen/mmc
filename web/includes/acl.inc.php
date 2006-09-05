<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

function existAclAttr($attr) {
global $aclArray;
  foreach ($aclArray as $items) {
    if (array_key_exists($attr,$items)) {
      return true;
    }
  }
  return false;
}

/**
 * return wich module correspond an attribute
 */
function getAclAttrModule($attr) {
global $aclArray;
  foreach ($aclArray as $key=>$items) {
    if (array_key_exists($attr,$items)) {
      return $key;
    }
  }
  return false;
}

function getAclAttr($attr) {
  if ($_SESSION["login"]=="root") {return "rw";}
  else { return $_SESSION["aclattr"][$attr]; }
}

function hasCorrectAcl($module,$submod,$action) {
    global $noAclArray;
    if ($noAclArray[$module][$submod][$action]==1) { return true; }
  if ($_SESSION["login"]=="root") {return true;}
  if ($_SESSION["acl"][$module][$submod][$action]["right"]) {return true;}
  return false;
}

function hasCorrectModuleAcl($module) {

  global $redirArray;
  // if you are root
  if ($_SESSION["login"]=="root") {return true;}

  //if you have one acces to the module
  if ($_SESSION["acl"][$module]) {return true;}

  if (!$redirArray[$module]) { return true; }

  return false;
}

function getDefaultPage() {
  $base = "";
  foreach(array_keys($_SESSION["acl"]) as $key => $value) {
    if ($value != "") {
      $base = $value;
      break;
    }
  }

  $submod = "";
  foreach(array_keys($_SESSION["acl"][$base]) as $key => $value) {
    if ($value != "") {
      $submod = $value;
      break;
    }
  }

  $action = "";
  foreach(array_keys($_SESSION["acl"][$base][$submod]) as $key => $value) {
    if ($value != "") {
      $action = $value;
      break;
    }
  }

 if (!$base) {
    return "index.php?error=".urlencode(_("You do not have required rights"));
 }

  return "main.php?module=$base&submod=$submod&action=$action";
}

?>