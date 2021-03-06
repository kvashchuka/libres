/*
   Copyright (C) 2011  Equinor ASA, Norway.

   The file 'obs_vector.h' is part of ERT - Ensemble based Reservoir Tool.

   ERT is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   ERT is distributed in the hope that it will be useful, but WITHOUT ANY
   WARRANTY; without even the implied warranty of MERCHANTABILITY or
   FITNESS FOR A PARTICULAR PURPOSE.

   See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
   for more details.
*/

#ifndef ERT_OBS_VECTOR_H
#define ERT_OBS_VECTOR_H


#include <time.h>

#include <ert/util/bool_vector.h>
#include <ert/util/int_vector.h>

#include <ert/sched/history.hpp>

#include <ert/config/conf.hpp>

#include <ert/ecl/ecl_sum.h>

#include <ert/enkf/enkf_fs.hpp>
#include <ert/enkf/enkf_types.hpp>
#include <ert/enkf/enkf_node.hpp>
#include <ert/enkf/enkf_state.hpp>
#include <ert/enkf/ensemble_config.hpp>
#include <ert/enkf/obs_data.hpp>
#include <ert/enkf/enkf_macros.hpp>
#include <ert/enkf/active_list.hpp>
#include <ert/enkf/time_map.hpp>
#include <ert/enkf/local_obsdata_node.hpp>

#ifdef __cplusplus
extern "C" {
#endif

  typedef void   (obs_free_ftype)                (void *);
  typedef void   (obs_get_ftype)                 (const void * , obs_data_type * , enkf_fs_type *, int , const active_list_type * );
  typedef void   (obs_meas_ftype)                (const void * , const void *, node_id_type , meas_data_type * , const active_list_type * );
  typedef void   (obs_user_get_ftype)            (void * , const char * , double * , double * , bool *);
  typedef void   (obs_update_std_scale_ftype)    (void * , double , const active_list_type * );
  typedef double (obs_chi2_ftype)                (const void * , const void *, node_id_type );

  typedef enum { GEN_OBS     = 1,
                 SUMMARY_OBS = 2,
                 BLOCK_OBS   = 3} obs_impl_type;

  typedef struct obs_vector_struct obs_vector_type;


  void                 obs_vector_free(obs_vector_type * );
  int                  obs_vector_get_num_active(const obs_vector_type * );
  bool                 obs_vector_iget_active(const obs_vector_type * , int );
  void                 obs_vector_iget_observations(const obs_vector_type *  , int  , obs_data_type * , const active_list_type * active_list, enkf_fs_type * fs);
  bool                 obs_vector_has_data( const obs_vector_type * obs_vector , const bool_vector_type * active_mask , enkf_fs_type * fs);
  void                 obs_vector_measure(const obs_vector_type *  , enkf_fs_type * fs, int report_step , const int_vector_type * ens_active_list , meas_data_type * , const active_list_type * active_list);
  const char         * obs_vector_get_state_kw(const obs_vector_type * );
  const char         * obs_vector_get_key(const obs_vector_type * );
  obs_impl_type        obs_vector_get_impl_type(const obs_vector_type * );
  const int_vector_type * obs_vector_get_step_list(const obs_vector_type * vector);
  void                 obs_vector_user_get(const obs_vector_type * obs_vector , const char * index_key , int report_step , double * value , double * std , bool * valid);
  int                  obs_vector_get_next_active_step(const obs_vector_type * , int );
  void               * obs_vector_iget_node(const obs_vector_type * , int );
  obs_vector_type    * obs_vector_alloc_from_GENERAL_OBSERVATION(const conf_instance_type *  , time_map_type * obs_time , const ensemble_config_type * );
  void                 obs_vector_load_from_SUMMARY_OBSERVATION(obs_vector_type * obs_vector , const conf_instance_type *  , time_map_type * obs_time , ensemble_config_type * );
  bool                 obs_vector_load_from_HISTORY_OBSERVATION(obs_vector_type * obs_vector , const conf_instance_type *  , time_map_type * obs_time , const history_type * , ensemble_config_type * , double std_cutoff );
  obs_vector_type    * obs_vector_alloc_from_BLOCK_OBSERVATION(const conf_instance_type *    , const ecl_grid_type * grid , time_map_type * obs_time , const ecl_sum_type * refcase , ensemble_config_type * );
  obs_vector_type    * obs_vector_alloc(obs_impl_type obs_type , const char * obs_key , enkf_config_node_type * config_node, int num_reports);
  void                 obs_vector_scale_std(obs_vector_type * obs_vector, const local_obsdata_node_type * local_node , double std_multiplier);
  void                 obs_vector_install_node(obs_vector_type * obs_vector , int obs_index , void * node );

  void                    obs_vector_ensemble_chi2(const obs_vector_type * obs_vector ,
                                                   enkf_fs_type * fs,
                                                   bool_vector_type * valid ,
                                                   int step1 , int step2 ,
                                                   int iens1 , int iens2 ,
                                                   double ** chi2);

  double                  obs_vector_total_chi2(const obs_vector_type * , enkf_fs_type * , int );
  enkf_config_node_type * obs_vector_get_config_node(const obs_vector_type * );
  const char            * obs_vector_get_obs_key( const obs_vector_type * obs_vector);
  local_obsdata_node_type * obs_vector_alloc_local_node(const obs_vector_type * obs_vector);



  UTIL_IS_INSTANCE_HEADER(obs_vector);
  UTIL_SAFE_CAST_HEADER(obs_vector);
  VOID_FREE_HEADER(obs_vector);


#ifdef __cplusplus
}
#endif
#endif
