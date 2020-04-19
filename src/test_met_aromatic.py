from pytest import mark, skip
from pandas import DataFrame, testing
from met_aromatic import MetAromatic


TEST_CODES = {
    '1l5l', '5wr6', '5i6u', '1q83', '4qo4', '4blz', '4nxw', '2xdb', '2acx',
    '3h0k', '4xff', '1xd1', '2n2u', '1yrs', '1sly', '4zk0', '3ki3', '5hml',
    '1yop', '1n6j', '1mnh', '1i0s', '5fhv', '3f1n', '5khc', '5khk', '2alf',
    '3dpc', '3skv', '6hwr', '2wm1', '3u53', '3mhk', '1bml', '4cx1', '4a64',
    '4jbx', '1ghp', '2r9h', '3omo', '1ccb', '4bwm', '5l6o', '3fg4', '3w30',
    '2zj1', '1b1y', '5gwn', '5uxe', '5pyc', '5azh', '5otc', '1th2', '4ncm',
    '3lqz', '6dbp', '1b4w', '4j4r', '5u6e', '4tog', '5lvg', '4fcd', '3uwx',
    '6hyh', '3u4s', '1yoj', '3t12', '4rlr', '2ggi', '3ps0', '4uvt', '5e35',
    '2xuc', '4u8m', '2lko', '2owg', '1ww6', '1wel', '5qb2', '3lcc', '2itl',
    '5jvv', '5hk5', '2fhb', '2zyh', '3q8n', '4h7k', '4pba', '5dsk', '2awm',
    '4lwb', '5ton', '4i74', '2a0l', '3vr1', '6ezq', '4ju4', '1y4p', '3t3i',
    '2x3u', '4pja', '5i7o', '1r0k', '6cj4', '5yq0', '4kd4', '3zxp', '3t6u',
    '3ix9', '4boy', '1h58', '3icj', '3ahd', '5eou', '2vef', '2kx6', '2qmz',
    '5c71', '4pfa', '6eiq', '5frw', '2vmn', '6bcn', '5u1j', '5kqd', '4aqt',
    '4zlo', '6jxq', '4d56', '4m7m', '2c68', '6fuh', '3b4r', '2ba2', '4y7p',
    '2qy2', '2mwy', '3e25', '2qs4', '1q1z', '6f71', '1nuf', '5ih5', '5tss',
    '3ug7', '3g3q', '5req', '4dma', '4h5v'
}


@mark.parametrize(
    "code",
    TEST_CODES
)
def test_metaromatic_algorithm_against_483_data(code, default_met_aromatic_parameters, get_483_control_data):
    df_control = get_483_control_data[get_483_control_data.PDBCODE == code]
    df_control = df_control.drop(['PDBCODE'], axis=1)
    df_control = df_control.reindex(sorted(df_control.columns), axis=1)
    df_control = df_control.sort_values(by='NORM')
    df_control = df_control.reset_index(drop=True)

    try:
        test_data = MetAromatic(
            code=code,
            cutoff_angle=default_met_aromatic_parameters['angle'],
            cutoff_distance=default_met_aromatic_parameters['distance'],
            chain=default_met_aromatic_parameters['chain'],
            model=default_met_aromatic_parameters['model']
        ).get_met_aromatic_interactions()

    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')

    df_test = DataFrame(
        test_data,
        columns=[
            'ARO', 'ARO RES', 'MET', 'MET RES',
            'NORM', 'MET-THETA', 'MET-PHI'
        ]
    )

    df_test = df_test.reindex(sorted(df_test.columns), axis=1)
    df_test = df_test.sort_values(by='NORM')
    df_test = df_test.reset_index(drop=True)
    df_test = df_test.astype({'MET RES': 'int64', 'ARO RES': 'int64'})
    testing.assert_frame_equal(df_control, df_test)
