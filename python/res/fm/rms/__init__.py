from .rms_config import RMSConfig
from .rms_run import RMSRun, RMSRunException


def run(
    iens,
    project,
    workflow,
    run_path="rms",
    target_file=None,
    export_path="rmsEXPORT",
    import_path="rmsIMPORT",
    version=None,
    readonly=True,
):
    run_object = RMSRun(
        iens,
        project,
        workflow,
        run_path=run_path,
        target_file=target_file,
        export_path=export_path,
        import_path=import_path,
        version=version,
        readonly=readonly,
    )
    run_object.run()
