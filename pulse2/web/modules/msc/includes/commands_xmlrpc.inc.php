<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: ajaxPackageFilter.php,v 1.1 2008/01/08 14:02:59 root Exp $
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

function count_all_commands_on_host_group($gid, $cmd_id, $filter, $history = 0) {
    return xmlCall('msc.count_all_commands_on_host_group', array($gid, $cmd_id, $filter, $history));
}

function get_all_commands_on_host_group($gid, $cmd_id, $min, $max, $filter, $history = 0) {
    return xmlCall('msc.get_all_commands_on_host_group', array($gid, $cmd_id, $min, $max, $filter, $history));
}

function get_all_commandsonhost_currentstate() {
    return xmlCall('msc.get_all_commandsonhost_currentstate');
}

function count_all_commandsonhost_by_currentstate($current_state, $filt = '') {
    return xmlCall('msc.count_all_commandsonhost_by_currentstate', array($current_state, $filt));
}

function get_all_commandsonhost_by_currentstate($current_state, $min = 0, $max = 10, $filt = '') {
    return xmlCall('msc.get_all_commandsonhost_by_currentstate', array($current_state, $min, $max, $filt));
}

function count_all_commandsonhost_by_type($type, $filter) {
    return xmlCall('msc.count_all_commandsonhost_by_type', array($type, $filter));
}

function get_all_commandsonhost_by_type($type, $min, $max, $filter) {
    return xmlCall('msc.get_all_commandsonhost_by_type', array($type, $min, $max, $filter));
}

function count_all_commands_on_group($gid, $filter, $history = 0) {
    return xmlCall('msc.count_all_commands_on_group', array($gid, $filter, $history));
}

function get_all_commands_on_group($gid, $min, $max, $filter, $history = 0) {
    return xmlCall('msc.get_all_commands_on_group', array($gid, $min, $max, $filter, $history));
}

function count_all_commands_on_host($uuid, $filter) {
    return xmlCall('msc.count_all_commands_on_host', array($uuid, $filter));
}

function get_all_commands_on_host($uuid, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_host', array($uuid, $min, $max, $filter));
}

function count_finished_commands_on_host($uuid, $filter) {
    return xmlCall('msc.count_finished_commands_on_host', array($uuid, $filter));
}

function get_finished_commands_on_host($uuid, $min, $max, $filter) {
    return xmlCall('msc.get_finished_commands_on_host', array($uuid, $min, $max, $filter));
}

function count_unfinished_commands_on_host($uuid, $filter) {
    return xmlCall('msc.count_unfinished_commands_on_host', array($uuid, $filter));
}

function get_unfinished_commands_on_host($uuid, $min, $max, $filter) {
    return xmlCall('msc.get_unfinished_commands_on_host', array($uuid, $min, $max, $filter));
}

function get_commands_on_host($coh_id) {
    return xmlCall('msc.get_commands_on_host', array($coh_id));
}

function get_target_for_coh($coh_id) {
    return xmlCall('msc.get_target_for_coh', array($coh_id));
}

function get_command_history($coh_id) {
    return xmlCall('msc.get_commands_history', array($coh_id));
}

function command_detail($cmd_id) {
    return xmlCall('msc.get_commands', array($cmd_id));
}

function add_command_api($pid, $target, $params, $p_api, $mode, $gid = null) {
    return xmlCall('msc.add_command_api', array($pid, $target, $params, $p_api, $mode, $gid));
}

function add_command_quick($cmd, $hosts, $desc, $gid = null) {
    return xmlCall('msc.add_command_quick', array($cmd, $hosts, $desc, $gid));
}

function get_id_command_on_host($id) {
    return xmlCall('msc.get_id_command_on_host', array($id));
}

/* Command on host handling */
function start_command_on_host($id) {
    return xmlCall('msc.start_command_on_host', array($id));
}
function stop_command_on_host($id) {
    return xmlCall('msc.stop_command_on_host', array($id));
}
function pause_command_on_host($id) {
    return xmlCall('msc.pause_command_on_host', array($id));
}
function restart_command_on_host($id) {
    return xmlCall('msc.restart_command_on_host', array($id));
}
/* /Command on host handling */



?>
