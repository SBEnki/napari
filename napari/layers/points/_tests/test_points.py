from copy import copy
from itertools import cycle, islice
from xml.etree.ElementTree import Element

import numpy as np
import pandas as pd
import pytest
from vispy.color import get_colormap

from napari.layers import Points
from napari.layers.points._points_utils import points_to_squares
from napari.utils.colormaps.standardize_color import transform_color


def _make_cycled_properties(values, length):
    """Helper function to make property values

    Parameters:
    -----------
    values :
        The values to be cycled.
    length : int
        The length of the resulting property array

    Returns:
    --------
    cycled_properties : np.ndarray
        The property array comprising the cycled values.
    """
    cycled_properties = np.array(list(islice(cycle(values), 0, length)))
    return cycled_properties


def test_empty_points():
    pts = Points()
    assert pts.data.shape == (0, 2)


def test_empty_points_with_properties():
    """ Test instantiating an empty Points layer with properties

    See: https://github.com/napari/napari/pull/1069
    """
    properties = {
        'label': np.array(['label1', 'label2']),
        'cont_prop': np.array([0], dtype=np.float),
    }
    pts = Points(properties=properties)
    current_props = {k: v[0] for k, v in properties.items()}
    np.testing.assert_equal(pts.current_properties, current_props)

    # verify the property datatype is correct
    assert pts.properties['cont_prop'].dtype == np.float

    # add two points and verify the default property was applied
    pts.add([10, 10])
    pts.add([20, 20])
    props = {
        'label': np.array(['label1', 'label1']),
        'cont_prop': np.array([0, 0], dtype=np.float),
    }
    np.testing.assert_equal(pts.properties, props)


def test_empty_points_with_properties_list():
    """ Test instantiating an empty Points layer with properties
    stored in a list

    See: https://github.com/napari/napari/pull/1069
    """
    properties = {'label': ['label1', 'label2'], 'cont_prop': [0]}
    pts = Points(properties=properties)
    current_props = {k: np.asarray(v[0]) for k, v in properties.items()}
    np.testing.assert_equal(pts.current_properties, current_props)

    # add two points and verify the default property was applied
    pts.add([10, 10])
    pts.add([20, 20])
    props = {
        'label': np.array(['label1', 'label1']),
        'cont_prop': np.array([0, 0], dtype=np.float),
    }
    np.testing.assert_equal(pts.properties, props)


def test_empty_layer_with_face_colorap():
    """ Test creating an empty layer where the face color is a colormap
    See: https://github.com/napari/napari/pull/1069
    """
    default_properties = {'point_type': np.array([1.5], dtype=np.float)}
    layer = Points(
        properties=default_properties,
        face_color='point_type',
        face_colormap='grays',
    )

    assert layer.face_color_mode == 'colormap'

    # verify the current_face_color is correct
    face_color = np.array([1, 1, 1, 1])
    assert np.all(layer._current_face_color == face_color)


def test_empty_layer_with_edge_colormap():
    """ Test creating an empty layer where the face color is a colormap
    See: https://github.com/napari/napari/pull/1069
    """
    default_properties = {'point_type': np.array([1.5], dtype=np.float)}
    layer = Points(
        properties=default_properties,
        edge_color='point_type',
        edge_colormap='grays',
    )

    assert layer.edge_color_mode == 'colormap'

    # verify the current_face_color is correct
    edge_color = np.array([1, 1, 1, 1])
    assert np.all(layer._current_edge_color == edge_color)


def test_random_points():
    """Test instantiating Points layer with random 2D data."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 10
    assert len(layer.selected_data) == 0


def test_integer_points():
    """Test instantiating Points layer with integer data."""
    shape = (10, 2)
    np.random.seed(0)
    data = np.random.randint(20, size=(10, 2))
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 10


def test_negative_points():
    """Test instantiating Points layer with negative data."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape) - 10
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 10


def test_empty_points_array():
    """Test instantiating Points layer with empty array."""
    shape = (0, 2)
    data = np.empty(shape)
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 0


def test_3D_points():
    """Test instantiating Points layer with random 3D data."""
    shape = (10, 3)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 10


def test_4D_points():
    """Test instantiating Points layer with random 4D data."""
    shape = (10, 4)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert np.all(layer.data == data)
    assert layer.ndim == shape[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 10


def test_changing_points():
    """Test changing Points data."""
    shape_a = (10, 2)
    shape_b = (20, 2)
    np.random.seed(0)
    data_a = 20 * np.random.random(shape_a)
    data_b = 20 * np.random.random(shape_b)
    layer = Points(data_a)
    layer.data = data_b
    assert np.all(layer.data == data_b)
    assert layer.ndim == shape_b[1]
    assert layer._view_data.ndim == 2
    assert len(layer.data) == 20


def test_selecting_points():
    """Test selecting points."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    layer.mode = 'select'
    data_to_select = {1, 2}
    layer.selected_data = data_to_select
    assert layer.selected_data == data_to_select

    # test switching to 3D
    layer.dims.ndisplay = 3
    assert layer.selected_data == data_to_select

    # select different points while in 3D mode
    other_data_to_select = {0}
    layer.selected_data = other_data_to_select
    assert layer.selected_data == other_data_to_select

    # selection should persist when going back to 2D mode
    layer.dims.ndisplay = 2
    assert layer.selected_data == other_data_to_select

    # selection should persist when switching between between select and pan_zoom
    layer.mode = 'pan_zoom'
    assert layer.selected_data == other_data_to_select
    layer.mode = 'select'
    assert layer.selected_data == other_data_to_select

    # add mode should clear the selection
    layer.mode = 'add'
    assert layer.selected_data == set()


def test_adding_points():
    """Test adding Points data."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert len(layer.data) == 10

    coord = [20, 20]
    layer.add(coord)
    assert len(layer.data) == 11
    assert np.all(layer.data[10] == coord)
    # the added point should be selected
    assert layer.selected_data == {10}

    # test adding multiple points
    coords = [[10, 10], [15, 15]]
    layer.add(coords)
    assert len(layer.data) == 13
    assert np.all(layer.data[11:, :] == coords)


def test_adding_points_to_empty():
    """Test adding Points data to empty."""
    shape = (0, 2)
    data = np.empty(shape)
    layer = Points(data)
    assert len(layer.data) == 0

    coord = [20, 20]
    layer.add(coord)
    assert len(layer.data) == 1
    assert np.all(layer.data[0] == coord)


def test_removing_selected_points():
    """Test selecting points."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)

    # With nothing selected no points should be removed
    layer.remove_selected()
    assert len(layer.data) == shape[0]

    # Select two points and remove them
    layer.selected_data = {0, 3}
    layer.remove_selected()
    assert len(layer.data) == shape[0] - 2
    assert len(layer.selected_data) == 0
    keep = [1, 2] + list(range(4, 10))
    assert np.all(layer.data == data[keep])

    # Select another point and remove it
    layer.selected_data = {4}
    layer.remove_selected()
    assert len(layer.data) == shape[0] - 3


def test_move():
    """Test moving points."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    unmoved = copy(data)
    layer = Points(data)

    # Move one point relative to an initial drag start location
    layer._move([0], [0, 0])
    layer._move([0], [10, 10])
    layer._drag_start = None
    assert np.all(layer.data[0] == unmoved[0] + [10, 10])
    assert np.all(layer.data[1:] == unmoved[1:])

    # Move two points relative to an initial drag start location
    layer._move([1, 2], [2, 2])
    layer._move([1, 2], np.add([2, 2], [-3, 4]))
    assert np.all(layer.data[1:2] == unmoved[1:2] + [-3, 4])


def test_changing_modes():
    """Test changing modes."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.mode == 'pan_zoom'
    assert layer.interactive is True

    layer.mode = 'add'
    assert layer.mode == 'add'
    assert layer.interactive is False

    layer.mode = 'select'
    assert layer.mode == 'select'
    assert layer.interactive is False

    layer.mode = 'pan_zoom'
    assert layer.mode == 'pan_zoom'
    assert layer.interactive is True

    with pytest.raises(ValueError):
        layer.mode = 'not_a_mode'


def test_name():
    """Test setting layer name."""
    np.random.seed(0)
    data = 20 * np.random.random((10, 2))
    layer = Points(data)
    assert layer.name == 'Points'

    layer = Points(data, name='random')
    assert layer.name == 'random'

    layer.name = 'pts'
    assert layer.name == 'pts'


def test_visiblity():
    """Test setting layer visiblity."""
    np.random.seed(0)
    data = 20 * np.random.random((10, 2))
    layer = Points(data)
    assert layer.visible is True

    layer.visible = False
    assert layer.visible is False

    layer = Points(data, visible=False)
    assert layer.visible is False

    layer.visible = True
    assert layer.visible is True


def test_opacity():
    """Test setting layer opacity."""
    np.random.seed(0)
    data = 20 * np.random.random((10, 2))
    layer = Points(data)
    assert layer.opacity == 1.0

    layer.opacity = 0.5
    assert layer.opacity == 0.5

    layer = Points(data, opacity=0.6)
    assert layer.opacity == 0.6

    layer.opacity = 0.3
    assert layer.opacity == 0.3


def test_blending():
    """Test setting layer blending."""
    np.random.seed(0)
    data = 20 * np.random.random((10, 2))
    layer = Points(data)
    assert layer.blending == 'translucent'

    layer.blending = 'additive'
    assert layer.blending == 'additive'

    layer = Points(data, blending='additive')
    assert layer.blending == 'additive'

    layer.blending = 'opaque'
    assert layer.blending == 'opaque'


def test_symbol():
    """Test setting symbol."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.symbol == 'disc'

    layer.symbol = 'cross'
    assert layer.symbol == 'cross'

    layer = Points(data, symbol='star')
    assert layer.symbol == 'star'


properties_array = {'point_type': _make_cycled_properties(['A', 'B'], 10)}
properties_list = {'point_type': list(_make_cycled_properties(['A', 'B'], 10))}


@pytest.mark.parametrize("properties", [properties_array, properties_list])
def test_properties(properties):
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data, properties=copy(properties))
    np.testing.assert_equal(layer.properties, properties)

    current_prop = {'point_type': np.array(['B'])}
    assert layer.current_properties == current_prop

    # test removing points
    layer.selected_data = {0, 1}
    layer.remove_selected()
    remove_properties = properties['point_type'][2::]
    assert len(layer.properties['point_type']) == (shape[0] - 2)
    assert np.all(layer.properties['point_type'] == remove_properties)

    # test selection of properties
    layer.selected_data = {0}
    selected_annotation = layer.current_properties['point_type']
    assert len(selected_annotation) == 1
    assert selected_annotation[0] == 'A'

    # test adding points with properties
    layer.add([10, 10])
    add_annotations = np.concatenate((remove_properties, ['A']), axis=0)
    assert np.all(layer.properties['point_type'] == add_annotations)

    # test copy/paste
    layer.selected_data = {0, 1}
    layer._copy_data()
    assert np.all(layer._clipboard['properties']['point_type'] == ['A', 'B'])

    layer._paste_data()
    paste_annotations = np.concatenate((add_annotations, ['A', 'B']), axis=0)
    assert np.all(layer.properties['point_type'] == paste_annotations)


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_adding_properties(attribute):
    """Test adding properties to an existing layer"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)

    # add properties
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    layer.properties = properties
    np.testing.assert_equal(layer.properties, properties)

    # add properties as a dataframe
    properties_df = pd.DataFrame(properties)
    layer.properties = properties_df
    np.testing.assert_equal(layer.properties, properties)

    # add properties as a dictionary with list values
    properties_list = {
        'point_type': list(_make_cycled_properties(['A', 'B'], shape[0]))
    }
    layer.properties = properties_list
    assert isinstance(layer.properties['point_type'], np.ndarray)

    # removing a property that was the _*_color_property should give a warning
    setattr(layer, f'_{attribute}_color_property', 'vector_type')
    properties_2 = {
        'not_vector_type': _make_cycled_properties(['A', 'B'], shape[0])
    }
    with pytest.warns(RuntimeWarning):
        layer.properties = properties_2


def test_properties_dataframe():
    """Test if properties can be provided as a DataFrame"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    properties_df = pd.DataFrame(properties)
    properties_df = properties_df.astype(properties['point_type'].dtype)
    layer = Points(data, properties=properties_df)
    np.testing.assert_equal(layer.properties, properties)


def test_add_points_with_properties_as_list():
    # test adding points initialized with properties as list
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {
        'point_type': list(_make_cycled_properties(['A', 'B'], shape[0]))
    }
    layer = Points(data, properties=copy(properties))

    coord = [18, 18]
    layer.add(coord)
    new_prop = {'point_type': np.append(properties['point_type'], 'B')}
    np.testing.assert_equal(layer.properties, new_prop)


def test_updating_points_properties():
    # test adding points initialized with properties
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    layer = Points(data, properties=copy(properties))

    layer.mode = 'select'
    layer.selected_data = [len(data) - 1]
    layer.current_properties = {'point_type': np.array(['A'])}

    updated_properties = properties
    updated_properties['point_type'][-1] = 'A'
    np.testing.assert_equal(layer.properties, updated_properties)


def test_points_errors():
    shape = (3, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)

    # try adding properties with the wrong number of properties
    with pytest.raises(ValueError):
        annotations = {'point_type': np.array(['A', 'B'])}
        Points(data, properties=copy(annotations))


def test_is_color_mapped():
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    annotations = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    layer = Points(data, properties=annotations)

    # giving the name of an annotation should return True
    assert layer._is_color_mapped('point_type')

    # giving a list should return false (i.e., could be an RGBA color)
    assert not layer._is_color_mapped([1, 1, 1, 1])

    # giving an ndarray should return false (i.e., could be an RGBA color)
    assert not layer._is_color_mapped(np.array([1, 1, 1, 1]))

    # give an invalid color argument
    with pytest.raises(ValueError):
        layer._is_color_mapped((123, 323))


def test_edge_width():
    """Test setting edge width."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.edge_width == 1

    layer.edge_width = 2
    assert layer.edge_width == 2

    layer = Points(data, edge_width=3)
    assert layer.edge_width == 3


def test_n_dimensional():
    """Test setting n_dimensional flag for 2D and 4D data."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.n_dimensional is False

    layer.n_dimensional = True
    assert layer.n_dimensional is True

    layer = Points(data, n_dimensional=True)
    assert layer.n_dimensional is True

    shape = (10, 4)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.n_dimensional is False

    layer.n_dimensional = True
    assert layer.n_dimensional is True

    layer = Points(data, n_dimensional=True)
    assert layer.n_dimensional is True


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_switch_color_mode(attribute):
    """Test switching between color modes"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    # create a continuous property with a known value in the last element
    continuous_prop = np.random.random((shape[0],))
    continuous_prop[-1] = 1
    properties = {
        'point_truthiness': continuous_prop,
        'point_type': _make_cycled_properties(['A', 'B'], shape[0]),
    }
    initial_color = [1, 0, 0, 1]
    color_cycle = ['red', 'blue']
    color_kwarg = f'{attribute}_color'
    colormap_kwarg = f'{attribute}_colormap'
    color_cycle_kwarg = f'{attribute}_color_cycle'
    args = {
        color_kwarg: initial_color,
        colormap_kwarg: 'gray',
        color_cycle_kwarg: color_cycle,
    }
    layer = Points(data, properties=properties, **args)

    layer_color_mode = getattr(layer, f'{attribute}_color_mode')
    layer_color = getattr(layer, f'{attribute}_color')
    assert layer_color_mode == 'direct'
    np.testing.assert_allclose(
        layer_color, np.repeat([initial_color], shape[0], axis=0)
    )

    # there should not be an edge_color_property
    color_property = getattr(layer, f'_{attribute}_color_property')
    assert color_property == ''

    # transitioning to colormap should raise a warning
    # because there isn't an edge color property yet and
    # the first property in points.properties is being automatically selected
    with pytest.warns(UserWarning):
        setattr(layer, f'{attribute}_color_mode', 'colormap')
    color_property = getattr(layer, f'_{attribute}_color_property')
    assert color_property == next(iter(properties))
    layer_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(layer_color[-1], [1, 1, 1, 1])

    # switch to color cycle
    setattr(layer, f'{attribute}_color_mode', 'cycle')
    setattr(layer, f'{attribute}_color', 'point_type')
    color = getattr(layer, f'{attribute}_color')
    layer_color = transform_color(color_cycle * int((shape[0] / 2)))
    np.testing.assert_allclose(color, layer_color)

    # switch back to direct, edge_colors shouldn't change
    setattr(layer, f'{attribute}_color_mode', 'direct')
    new_edge_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(new_edge_color, color)


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_colormap_without_properties(attribute):
    """Setting the colormode to colormap should raise an exception"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)

    with pytest.raises(ValueError):
        setattr(layer, f'{attribute}_color_mode', 'colormap')


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_colormap_with_categorical_properties(attribute):
    """Setting the colormode to colormap should raise an exception"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    layer = Points(data, properties=properties)

    with pytest.raises(TypeError):
        setattr(layer, f'{attribute}_color_mode', 'colormap')


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_add_colormap(attribute):
    """Test  directly adding a vispy Colormap object"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    annotations = {'point_type': _make_cycled_properties([0, 1.5], shape[0])}
    color_kwarg = f'{attribute}_color'
    colormap_kwarg = f'{attribute}_colormap'
    args = {color_kwarg: 'point_type', colormap_kwarg: 'viridis'}
    layer = Points(data, properties=annotations, **args)

    setattr(layer, f'{attribute}_colormap', get_colormap('gray'))
    layer_colormap = getattr(layer, f'{attribute}_colormap')
    assert layer_colormap[0] == 'unknown_colormap'


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_color_direct(attribute: str):
    """Test setting colors directly"""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer_kwargs = {f'{attribute}_color': 'black'}
    layer = Points(data, **layer_kwargs)
    color_array = transform_color(['black'] * shape[0])
    current_color = getattr(layer, f'current_{attribute}_color')
    layer_color = getattr(layer, f'{attribute}_color')
    assert current_color == 'black'
    assert len(layer.edge_color) == shape[0]
    np.testing.assert_allclose(color_array, layer_color)

    # With no data selected changing color has no effect
    setattr(layer, f'current_{attribute}_color', 'blue')
    current_color = getattr(layer, f'current_{attribute}_color')
    assert current_color == 'blue'
    np.testing.assert_allclose(color_array, layer_color)

    # Select data and change edge color of selection
    selected_data = {0, 1}
    layer.selected_data = {0, 1}
    current_color = getattr(layer, f'current_{attribute}_color')
    assert current_color == 'black'
    setattr(layer, f'current_{attribute}_color', 'green')
    colorarray_green = transform_color(['green'] * len(layer.selected_data))
    color_array[list(selected_data)] = colorarray_green
    layer_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(color_array, layer_color)

    # Add new point and test its color
    coord = [18, 18]
    layer.selected_data = {}
    setattr(layer, f'current_{attribute}_color', 'blue')
    layer.add(coord)
    color_array = np.vstack([color_array, transform_color('blue')])
    layer_color = getattr(layer, f'{attribute}_color')
    assert len(layer_color) == shape[0] + 1
    np.testing.assert_allclose(color_array, layer_color)

    # Check removing data adjusts colors correctly
    layer.selected_data = {0, 2}
    layer.remove_selected()
    assert len(layer.data) == shape[0] - 1

    layer_color = getattr(layer, f'{attribute}_color')
    assert len(layer_color) == shape[0] - 1
    np.testing.assert_allclose(
        layer_color, np.vstack((color_array[1], color_array[3:])),
    )


color_cycle_str = ['red', 'blue']
color_cycle_rgb = [[1, 0, 0], [0, 0, 1]]
color_cycle_rgba = [[1, 0, 0, 1], [0, 0, 1, 1]]


@pytest.mark.parametrize("attribute", ['edge', 'face'])
@pytest.mark.parametrize(
    "color_cycle", [color_cycle_str, color_cycle_rgb, color_cycle_rgba],
)
def test_color_cycle(attribute, color_cycle):
    """Test setting edge/face color with a color cycle list"""
    # create Points using list color cycle
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    points_kwargs = {
        'properties': properties,
        f'{attribute}_color': 'point_type',
        f'{attribute}_color_cycle': color_cycle,
    }
    layer = Points(data, **points_kwargs)

    assert layer.properties == properties
    color_array = transform_color(
        list(islice(cycle(color_cycle), 0, shape[0]))
    )
    layer_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(layer_color, color_array)

    # Add new point and test its color
    coord = [18, 18]
    layer.selected_data = {0}
    layer.add(coord)
    layer_color = getattr(layer, f'{attribute}_color')
    assert len(layer_color) == shape[0] + 1
    np.testing.assert_allclose(
        layer_color, np.vstack((color_array, transform_color('red'))),
    )

    # Check removing data adjusts colors correctly
    layer.selected_data = {0, 2}
    layer.remove_selected()
    assert len(layer.data) == shape[0] - 1

    layer_color = getattr(layer, f'{attribute}_color')
    assert len(layer_color) == shape[0] - 1
    np.testing.assert_allclose(
        layer_color,
        np.vstack((color_array[1], color_array[3:], transform_color('red'))),
    )

    # refresh colors
    layer.refresh_colors(update_color_mapping=True)


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_add_color_cycle_to_empty_layer(attribute):
    """ Test adding a point to an empty layer when edge/face color is a color cycle

    See: https://github.com/napari/napari/pull/1069
    """
    default_properties = {'point_type': np.array(['A'])}
    color_cycle = ['red', 'blue']
    points_kwargs = {
        'properties': default_properties,
        f'{attribute}_color': 'point_type',
        f'{attribute}_color_cycle': color_cycle,
    }
    layer = Points(**points_kwargs)

    # verify the current_edge_color is correct
    expected_color = transform_color(color_cycle[0])
    current_color = getattr(layer, f'_current_{attribute}_color')
    np.testing.assert_allclose(current_color, expected_color)

    # add a point
    layer.add([10, 10])
    props = {'point_type': np.array(['A'])}
    expected_color = np.array([[1, 0, 0, 1]])
    np.testing.assert_equal(layer.properties, props)
    attribute_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(attribute_color, expected_color)

    # add a point with a new property
    layer.selected_data = []
    layer.current_properties = {'point_type': np.array(['B'])}
    layer.add([12, 12])
    new_color = np.array([0, 0, 1, 1])
    expected_color = np.vstack((expected_color, new_color))
    new_properties = {'point_type': np.array(['A', 'B'])}
    attribute_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(attribute_color, expected_color)
    np.testing.assert_equal(layer.properties, new_properties)


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_adding_value_color_cycle(attribute):
    """ Test that adding values to properties used to set a color cycle
    and then calling Points.refresh_colors() performs the update and adds the
    new value to the face/edge_color_cycle_map.

    See: https://github.com/napari/napari/issues/988
    """
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties(['A', 'B'], shape[0])}
    color_cycle = ['red', 'blue']
    points_kwargs = {
        'properties': properties,
        f'{attribute}_color': 'point_type',
        f'{attribute}_color_cycle': color_cycle,
    }
    layer = Points(data, **points_kwargs)

    # make point 0 point_type C
    point_types = layer.properties['point_type']
    point_types[0] = 'C'
    layer.properties['point_type'] = point_types
    layer.refresh_colors(update_color_mapping=False)

    color_cycle_map = getattr(layer, f'{attribute}_color_cycle_map')
    color_map_keys = [*color_cycle_map]
    assert 'C' in color_map_keys


@pytest.mark.parametrize("attribute", ['edge', 'face'])
def test_color_colormap(attribute):
    """Test setting edge/face color with a colormap"""
    # create Points using with a colormap
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    properties = {'point_type': _make_cycled_properties([0, 1.5], shape[0])}
    points_kwargs = {
        'properties': properties,
        f'{attribute}_color': 'point_type',
        f'{attribute}_colormap': 'gray',
    }
    layer = Points(data, **points_kwargs)
    assert layer.properties == properties
    color_mode = getattr(layer, f'{attribute}_color_mode')
    assert color_mode == 'colormap'
    color_array = transform_color(['black', 'white'] * int((shape[0] / 2)))
    attribute_color = getattr(layer, f'{attribute}_color')
    assert np.all(attribute_color == color_array)

    # change the color cycle - face_color should not change
    setattr(layer, f'{attribute}_color_cycle', ['red', 'blue'])
    attribute_color = getattr(layer, f'{attribute}_color')
    assert np.all(attribute_color == color_array)

    # Add new point and test its color
    coord = [18, 18]
    layer.selected_data = {0}
    layer.add(coord)
    attribute_color = getattr(layer, f'{attribute}_color')
    assert len(attribute_color) == shape[0] + 1
    np.testing.assert_allclose(
        attribute_color, np.vstack((color_array, transform_color('black'))),
    )

    # Check removing data adjusts colors correctly
    layer.selected_data = {0, 2}
    layer.remove_selected()
    assert len(layer.data) == shape[0] - 1
    attribute_color = getattr(layer, f'{attribute}_color')
    assert len(attribute_color) == shape[0] - 1
    np.testing.assert_allclose(
        attribute_color,
        np.vstack(
            (color_array[1], color_array[3:], transform_color('black'),)
        ),
    )

    # adjust the clims
    setattr(layer, f'{attribute}_contrast_limits', (0, 3))
    layer.refresh_colors(update_color_mapping=False)
    attribute_color = getattr(layer, f'{attribute}_color')
    np.testing.assert_allclose(attribute_color[-2], [0.5, 0.5, 0.5, 1])

    # change the colormap
    new_colormap = 'viridis'
    setattr(layer, f'{attribute}_colormap', new_colormap)
    attribute_colormap = getattr(layer, f'{attribute}_colormap')
    assert attribute_colormap[1] == get_colormap(new_colormap)


def test_size():
    """Test setting size with scalar."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.unique(layer.size)[0] == 10

    # Add a new point, it should get current size
    coord = [17, 17]
    layer.add(coord)
    assert layer.size.shape == (11, 2)
    assert np.unique(layer.size)[0] == 10

    # Setting size affects newly added points not current points
    layer.current_size = 20
    assert layer.current_size == 20
    assert layer.size.shape == (11, 2)
    assert np.unique(layer.size)[0] == 10

    # Add new point, should have new size
    coord = [18, 18]
    layer.add(coord)
    assert layer.size.shape == (12, 2)
    assert np.unique(layer.size[:11])[0] == 10
    assert np.all(layer.size[11] == [20, 20])

    # Select data and change size
    layer.selected_data = {0, 1}
    assert layer.current_size == 10
    layer.current_size = 16
    assert layer.size.shape == (12, 2)
    assert np.unique(layer.size[2:11])[0] == 10
    assert np.unique(layer.size[:2])[0] == 16

    # Select data and size changes
    layer.selected_data = {11}
    assert layer.current_size == 20


def test_size_with_arrays():
    """Test setting size with arrays."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    sizes = 5 * np.random.random(shape)
    layer.size = sizes
    assert np.all(layer.size == sizes)

    # Test broadcasting of sizes
    sizes = [5, 5]
    layer.size = sizes
    assert np.all(layer.size[0] == sizes)

    # Test broadcasting of transposed sizes
    sizes = np.random.randint(low=1, high=5, size=shape[::-1])
    layer.size = sizes
    np.testing.assert_equal(layer.size, sizes.T)

    # Un-broadcastable array should raise an exception
    bad_sizes = np.random.randint(low=1, high=5, size=(3, 8))
    with pytest.raises(ValueError):
        layer.size = bad_sizes

    # Create new layer with new size array data
    sizes = 5 * np.random.random(shape)
    layer = Points(data, size=sizes)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.all(layer.size == sizes)

    # Create new layer with new size array data
    sizes = [5, 5]
    layer = Points(data, size=sizes)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.all(layer.size[0] == sizes)

    # Add new point, should have new size
    coord = [18, 18]
    layer.current_size = 13
    layer.add(coord)
    assert layer.size.shape == (11, 2)
    assert np.unique(layer.size[:10])[0] == 5
    assert np.all(layer.size[10] == [13, 13])

    # Select data and change size
    layer.selected_data = {0, 1}
    assert layer.current_size == 5
    layer.current_size = 16
    assert layer.size.shape == (11, 2)
    assert np.unique(layer.size[2:10])[0] == 5
    assert np.unique(layer.size[:2])[0] == 16

    # Check removing data adjusts colors correctly
    layer.selected_data = {0, 2}
    layer.remove_selected()
    assert len(layer.data) == 9
    assert len(layer.size) == 9
    assert np.all(layer.size[0] == [16, 16])
    assert np.all(layer.size[1] == [5, 5])


def test_size_with_3D_arrays():
    """Test setting size with 3D arrays."""
    shape = (10, 3)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    data[:2, 0] = 0
    layer = Points(data)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.unique(layer.size)[0] == 10

    sizes = 5 * np.random.random(shape)
    layer.size = sizes
    assert np.all(layer.size == sizes)

    # Test broadcasting of sizes
    sizes = [1, 5, 5]
    layer.size = sizes
    assert np.all(layer.size[0] == sizes)

    # Create new layer with new size array data
    sizes = 5 * np.random.random(shape)
    layer = Points(data, size=sizes)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.all(layer.size == sizes)

    # Create new layer with new size array data
    sizes = [1, 5, 5]
    layer = Points(data, size=sizes)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.all(layer.size[0] == sizes)

    # Add new point, should have new size in last dim only
    coord = [4, 18, 18]
    layer.current_size = 13
    layer.add(coord)
    assert layer.size.shape == (11, 3)
    assert np.unique(layer.size[:10, 1:])[0] == 5
    assert np.all(layer.size[10] == [1, 13, 13])

    # Select data and change size
    layer.selected_data = {0, 1}
    assert layer.current_size == 5
    layer.current_size = 16
    assert layer.size.shape == (11, 3)
    assert np.unique(layer.size[2:10, 1:])[0] == 5
    assert np.all(layer.size[0] == [16, 16, 16])

    # Create new 3D layer with new 2D points size data
    sizes = [0, 5, 5]
    layer = Points(data, size=sizes)
    assert layer.current_size == 10
    assert layer.size.shape == shape
    assert np.all(layer.size[0] == sizes)

    # Add new point, should have new size only in last 2 dimensions
    coord = [4, 18, 18]
    layer.current_size = 13
    layer.add(coord)
    assert layer.size.shape == (11, 3)
    assert np.all(layer.size[10] == [0, 13, 13])

    # Select data and change size
    layer.selected_data = {0, 1}
    assert layer.current_size == 5
    layer.current_size = 16
    assert layer.size.shape == (11, 3)
    assert np.unique(layer.size[2:10, 1:])[0] == 5
    assert np.all(layer.size[0] == [0, 16, 16])


def test_copy_and_paste():
    """Test copying and pasting selected points."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    # Clipboard starts empty
    assert layer._clipboard == {}

    # Pasting empty clipboard doesn't change data
    layer._paste_data()
    assert len(layer.data) == 10

    # Copying with nothing selected leave clipboard empty
    layer._copy_data()
    assert layer._clipboard == {}

    # Copying and pasting with two points selected adds to clipboard and data
    layer.selected_data = {0, 1}
    layer._copy_data()
    layer._paste_data()
    assert len(layer._clipboard.keys()) > 0
    assert len(layer.data) == shape[0] + 2
    assert np.all(layer.data[:2] == layer.data[-2:])

    # Pasting again adds two more points to data
    layer._paste_data()
    assert len(layer.data) == shape[0] + 4
    assert np.all(layer.data[:2] == layer.data[-2:])

    # Unselecting everything and copying and pasting will empty the clipboard
    # and add no new data
    layer.selected_data = {}
    layer._copy_data()
    layer._paste_data()
    assert layer._clipboard == {}
    assert len(layer.data) == shape[0] + 4


def test_value():
    """Test getting the value of the data at the current coordinates."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    data[-1] = [0, 0]
    layer = Points(data)
    value = layer.get_value()
    assert layer.coordinates == (0, 0)
    assert value == 9

    layer.data = layer.data + 20
    value = layer.get_value()
    assert value is None


def test_message():
    """Test converting value and coords to message."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    data[-1] = [0, 0]
    layer = Points(data)
    msg = layer.get_message()
    assert type(msg) == str


def test_thumbnail():
    """Test the image thumbnail for square data."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    data[0] = [0, 0]
    data[-1] = [20, 20]
    layer = Points(data)
    layer._update_thumbnail()
    assert layer.thumbnail.shape == layer._thumbnail_shape


def test_thumbnail_with_n_points_greater_than_max():
    """Test thumbnail generation with n_points > _max_points_thumbnail

    see: https://github.com/napari/napari/pull/934
    """
    # 2D
    max_points = Points._max_points_thumbnail * 2
    bigger_data = np.random.randint(10, 100, (max_points, 2))
    big_layer = Points(bigger_data)
    big_layer._update_thumbnail()
    assert big_layer.thumbnail.shape == big_layer._thumbnail_shape

    # #3D
    bigger_data_3d = np.random.randint(10, 100, (max_points, 3))
    bigger_layer_3d = Points(bigger_data_3d)
    bigger_layer_3d.dims.ndisplay = 3
    bigger_layer_3d._update_thumbnail()
    assert bigger_layer_3d.thumbnail.shape == bigger_layer_3d._thumbnail_shape


def test_xml_list():
    """Test the xml generation."""
    shape = (10, 2)
    np.random.seed(0)
    data = 20 * np.random.random(shape)
    layer = Points(data)
    xml = layer.to_xml_list()
    assert type(xml) == list
    assert len(xml) == shape[0]
    assert np.all([type(x) == Element for x in xml])


def test_view_data():
    coords = np.array([[0, 1, 1], [0, 2, 2], [1, 3, 3], [3, 3, 3]])
    layer = Points(coords)

    layer.dims.set_point(0, 0)
    assert np.all(
        layer._view_data == coords[np.ix_([0, 1], layer.dims.displayed)]
    )

    layer.dims.set_point(0, 1)
    assert np.all(
        layer._view_data == coords[np.ix_([2], layer.dims.displayed)]
    )

    layer.dims.ndisplay = 3
    assert np.all(layer._view_data == coords)


def test_view_size():
    coords = np.array([[0, 1, 1], [0, 2, 2], [1, 3, 3], [3, 3, 3]])
    sizes = np.array([[3, 5, 5], [3, 5, 5], [3, 3, 3], [2, 2, 3]])
    layer = Points(coords, size=sizes, n_dimensional=False)

    layer.dims.set_point(0, 0)
    assert np.all(
        layer._view_size == sizes[np.ix_([0, 1], layer.dims.displayed)]
    )

    layer.dims.set_point(0, 1)
    assert np.all(layer._view_size == sizes[np.ix_([2], layer.dims.displayed)])

    layer.n_dimensional = True
    assert len(layer._view_size) == 3

    # test a slice with no points
    layer.n_dimensional = False
    layer.dims.set_point(0, 2)
    assert np.all(layer._view_size == [])


def test_view_colors():
    coords = [[0, 1, 1], [0, 2, 2], [1, 3, 3], [3, 3, 3]]
    face_color = np.array(
        [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1]]
    )
    edge_color = np.array(
        [[0, 0, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]
    )

    layer = Points(coords, face_color=face_color, edge_color=edge_color)
    layer.dims.set_point(0, 0)
    print(layer.face_color)
    print(layer._view_face_color)
    assert np.all(layer._view_face_color == face_color[[0, 1]])
    assert np.all(layer._view_edge_color == edge_color[[0, 1]])

    layer.dims.set_point(0, 1)
    assert np.all(layer._view_face_color == face_color[[2]])
    assert np.all(layer._view_edge_color == edge_color[[2]])

    # view colors should return empty array if there are no points
    layer.dims.set_point(0, 2)
    assert len(layer._view_face_color) == 0
    assert len(layer._view_edge_color) == 0


def test_interaction_box():
    """Test the boxes calculated for selected points"""
    data = [[3, 3]]
    size = 2
    layer = Points(data, size=size)

    # get a box with no points selected
    index = []
    box = layer.interaction_box(index)
    assert box is None

    # get a box with a point selected
    index = [0]
    expected_box = points_to_squares(data, size)
    box = layer.interaction_box(index)
    np.all([np.isin(p, expected_box) for p in box])
