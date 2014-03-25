from ert.enkf.plot import DataFetcher, ObservationGenDataFetcher, BlockObservationDataFetcher, EnsembleDataFetcher
from ert.enkf.plot_data import PcaPlotData
from ert.enkf.enums import EnkfStateType, RealizationStateEnum, EnkfObservationImplementationType
from ert.enkf import LocalObsdata, LocalObsdataNode, EnkfLinalg, MeasData, ObsData
from ert.util import Matrix, BoolVector
from ert_gui.models.connectors.plot.data_type_keys_model import DataTypeKeysModel


class PcaDataFetcher(DataFetcher):
    def __init__(self, ert):
        super(PcaDataFetcher, self).__init__(ert)

    def fetchSupportedKeys(self):
        summary_keys = EnsembleDataFetcher(self.ert()).getSupportedKeys()

        keys = []
        for key in summary_keys:
            obs_keys = self.ert().ensembleConfig().getNode(key).getObservationKeys()
            if len(obs_keys) > 0:
                keys.append(key)

        keys += BlockObservationDataFetcher(self.ert()).getSupportedKeys()
        keys += ObservationGenDataFetcher(self.ert()).getSupportedKeys()

        return keys


    def truncationOrNumberOfComponents(self, truncation_or_ncomp):
        """ @rtype: (float, int) """
        truncation = -1
        ncomp = -1

        if truncation_or_ncomp < 1:
            truncation = truncation_or_ncomp
        else:
            ncomp = int(truncation_or_ncomp)

        return truncation, ncomp


    def calculatePrincipalComponent(self, fs, local_obsdata, truncation_or_ncomp=3):
        pc = Matrix(1, 1)
        pc_obs = Matrix(1, 1)

        state_map = fs.getStateMap()
        ens_mask = BoolVector(False, self.ert().getEnsembleSize())
        state_map.selectMatching(ens_mask, RealizationStateEnum.STATE_HAS_DATA)
        active_list = BoolVector.createActiveList(ens_mask)

        if len(active_list) > 0:
            state = EnkfStateType.FORECAST
            ensemble = self.ert().getEnsembleConstant()
            meas_data = MeasData(active_list)
            obs_data = ObsData()

            self.ert().getObservations().getObservationAndMeasureData(fs, local_obsdata, state, active_list, meas_data, obs_data)

            active_size = len(obs_data)
            S = meas_data.createS(active_size)
            D_obs = obs_data.createDobs(active_size)

            truncation, ncomp = self.truncationOrNumberOfComponents(truncation_or_ncomp)

            obs_data.scale(S, D_obs=D_obs)
            EnkfLinalg.calculatePrincipalComponents(S, D_obs, truncation, ncomp, pc, pc_obs)

            return PcaPlotData(local_obsdata.getName(), pc, pc_obs)

        return None


    def getObsKeys(self, data_key , fs):
        ensemble_data_fetcher = EnsembleDataFetcher(self.ert())
        block_observation_data_fetcher = BlockObservationDataFetcher(self.ert())
        gen_data_observation_data_fetcher = ObservationGenDataFetcher(self.ert())
        tmpList = []

        if ensemble_data_fetcher.supportsKey(data_key):
            tmpList += self.ert().ensembleConfig().getNode(data_key).getObservationKeys()
        elif block_observation_data_fetcher.supportsKey(data_key):
            tmpList += [data_key]
        elif gen_data_observation_data_fetcher.supportsKey(data_key):
            tmpList += gen_data_observation_data_fetcher.getAllTmpListForKey(data_key)
        else:
            if DataTypeKeysModel().isCustomPcaKeys(data_key):
                observations = self.ert().getObservations()
                summary_obs_keys = observations.getTypedKeylist(EnkfObservationImplementationType.SUMMARY_OBS)
                gen_data_obs_keys =  observations.getTypedKeylist(EnkfObservationImplementationType.GEN_OBS)
                block_obs_keys =  observations.getTypedKeylist(EnkfObservationImplementationType.BLOCK_OBS)

                summary_obs_keys = [key for key in summary_obs_keys]
                gen_data_obs_keys = [key for key in gen_data_obs_keys]
                block_obs_keys = [key for key in block_obs_keys]
                
                tmpList = summary_obs_keys + gen_data_obs_keys# + block_obs_keys


        activeMask = BoolVector(True, self.ert().getEnsembleSize())
        ertObs = self.ert().getObservations()

        obsKeys = []
        for obs_key in tmpList:
            obsVector = ertObs[obs_key]
            if obsVector.hasData( activeMask , fs ):
                obsKeys.append( obs_key )
        return obsKeys



    def fetchData(self, key, case=None):
        data = {"x": None,
                "y": None,
                "obs_y": None,
                "min_y": None,
                "max_y": None,
                "min_x": None,
                "max_x": None}

        fs = self.ert().getEnkfFsManager().getFileSystem(case)
        obs_keys = self.getObsKeys(key,fs)

        step_1 = 0
        step_2 = self.ert().getHistoryLength()

        local_obsdata = LocalObsdata("PCA Observations %s" % case)

        for obs_key in obs_keys:
            if not obs_key in local_obsdata:
                obs_node = LocalObsdataNode(obs_key)
                obs_node.addRange(step_1, step_2)
                local_obsdata.addNode(obs_node)

        if len(local_obsdata) > 0:
            pca_data = self.calculatePrincipalComponent(fs, local_obsdata)

            data["x"] = []
            data["y"] = []
            data["obs_y"] = []

            data["min_x"] = 1
            data["max_x"] = len(pca_data)

            component_number = 0
            for pca_vector in pca_data:
                component_number += 1
                data["x"].append(component_number)

                obs_y = pca_vector.getObservation()

                if data["min_y"] is None or data["min_y"] > obs_y:
                    data["min_y"] = obs_y

                if data["max_y"] is None or data["max_y"] < obs_y:
                    data["max_y"] = obs_y

                data["obs_y"].append(obs_y)
                for index, value in enumerate(pca_vector):
                    if len(data["y"]) == index:
                        data["y"].append([])

                    y = data["y"][index]
                    y.append(value)

                    if data["min_y"] is None or data["min_y"] > value:
                        data["min_y"] = value

                    if data["max_y"] is None or data["max_y"] < value:
                        data["max_y"] = value

        return data
