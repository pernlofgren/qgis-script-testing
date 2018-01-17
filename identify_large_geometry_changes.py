##Original_Layer=vector
##Updated_Layer=vector
##Original_ID_Field=field Original_Layer
##Updated_ID_Field=field Updated_Layer
##Buffer_Distance=number 25
##Min_Length_Outside_Buffer=number 50
##QA_Large_Changes_Original=output vector
##QA_Large_Changes_Updated=output vector

import processing
from PyQt4.QtCore import QVariant

from qgis.core import (
    QgsField, QgsFields, QgsVectorFileWriter, QgsFeature,
    QgsFeatureRequest, QgsExpression, QgsGeometry, QgsVectorLayer
)
from qgis.utils import QGis

# Set up input variables:
original_lyr = processing.getObjectFromUri(Original_Layer)
updated_lyr = processing.getObjectFromUri(Updated_Layer)
original_id_field = Original_ID_Field
updated_id_field = Updated_ID_Field
buffer_distance = Buffer_Distance
min_length_outside_buffer = Min_Length_Outside_Buffer
output_of_original_lyr = QA_Large_Changes_Original
output_of_updated_lyr = QA_Large_Changes_Updated


def buffer(in_layer, buffer_distance):
    """
    A fixed distance buffering

    @param  in_layer:          Layer to buffer
    @type   in_layer:          QgsVectorLayer
    @param  buffer_distance:   Buffer distance
    @type   buffer_distance:   integer

    @return:    Buffered Layer
    @rtype:     QgsVectorLayer
    """
    buffering = processing.runalg(
        'qgis:fixeddistancebuffer', in_layer, buffer_distance, 10, False, None, progress=None)
    out_layer = processing.getObject(buffering['OUTPUT'])
    return out_layer


def find_changes(line_layer, buf_layer, line_id_col, buf_id_col, writer, remain_fields):
    """
    Find the geometry difference of the line_layer and the buf_layer,
    line_layer features that fall outside of the buf_layer are copied into the
    output layer.

    If part of a feature is within the buffer but part of it is not, the
    feature is split and only the part that outside of the buffer is copied.

    If the output feature happens to be multipart, EACH part of the feature
    is compared against the length tolerance. Only parts exceed the tolerance
    are kept. Then all parts are merged back into one feature.

    So in the output layer, features maybe of singleparts or multipart.
    @param  line_layer:        Layer
    @type   line_layer:        QgsVectorLayer
    @param  buf_layer:         Buffer Layer
    @type   buf_layer:         QgsVectorLayer
    @param  line_id_col:       Line id column name
    @type   line_id_col:       string
    @param  buf_id_col:        Buffer id column name
    @type   buf_id_col:        string
    @param  writer:            Writer of layer
    @type   writer:            QgsVectorFileWriter
    @param  remain_fields:     List of fields
    @type   remain_fields:     list

    @return:    Resulting ids
    @rtype:     list
    """
    result_ids = []
    out_feat = QgsFeature()

    for line_feat in line_layer.getFeatures():

        if line_feat[line_id_col] != 0:

            expr = QgsExpression('{} = {}'.format(buf_id_col, line_feat[line_id_col]))
            for buf_feat in buf_layer.getFeatures(QgsFeatureRequest(expr)):

                if not line_feat.geometry().within(buf_feat.geometry()):

                    diff_geom = line_feat.geometry().difference(buf_feat.geometry())

                    if diff_geom.isMultipart():

                        geom_multi = diff_geom.asMultiPolyline()
                        updated_geom_multi = []

                        for i in geom_multi:

                            geom_single = QgsGeometry.fromPolyline(i)
                            if geom_single.length() >= 50:
                                updated_geom_multi.append(i)

                        if updated_geom_multi:
                            out_feat.setGeometry(QgsGeometry.fromMultiPolyline(updated_geom_multi))
                            attrs = ["large change", "Not Checked", ""]
                            for remain_field in remain_fields:
                                attrs.append(line_feat[remain_field])
                            out_feat.setAttributes(attrs)
                            writer.addFeature(out_feat)
                            result_ids.append(int(line_feat[line_id_col]))
                    else:

                        if diff_geom.length() >= 50:
                            out_feat.setGeometry(diff_geom)
                            attrs = ["large change", "Not Checked", ""]
                            for remain_field in remain_fields:
                                attrs.append(line_feat[remain_field])
                            out_feat.setAttributes(attrs)
                            writer.addFeature(out_feat)
                            result_ids.append(int(line_feat[line_id_col]))
    return result_ids


def write_changes_to_output(in_layer, id_field, first, second):
    """
    Add features to in layer

    @param  in_layer:   Layer to add features to
    @type   in_layer:   QgsVectorLayer
    @param  id_field:   Unique id field name
    @type   id_field:   string
    @param  first:      Ids of changes in in_layer
    @type   first:      list
    @param  second:     Ids of changes in comparison layer
    @type   second:     list
    """
    in_layer.startEditing()
    for result_id in first:
        if result_id not in second:
            request = QgsFeatureRequest().setFilterExpression('{} = {}'.format(id_field, result_id))
            for feat in in_layer.getFeatures(request):
                in_layer.dataProvider().deleteFeatures([feat.id()])
    in_layer.commitChanges()


# Add 3 new fields to new layer
original_remain_fields = []
original_fields = QgsFields()
original_fields.append(QgsField("error_type", QVariant.String))
original_fields.append(QgsField("error_stat", QVariant.String))
original_fields.append(QgsField("error_comm", QVariant.String))

updated_remain_fields = []
updated_fields = QgsFields()
updated_fields.append(QgsField("error_type", QVariant.String))
updated_fields.append(QgsField("error_stat", QVariant.String))
updated_fields.append(QgsField("error_comm", QVariant.String))

for field in original_lyr.fields():
    original_fields.append(field)
    original_remain_fields.append(field.name())

for field in updated_lyr.fields():
    updated_fields.append(field)
    updated_remain_fields.append(field.name())

original_writer = QgsVectorFileWriter(
    output_of_original_lyr, None, original_fields, QGis.WKBLineString, original_lyr.crs())
updated_writer = QgsVectorFileWriter(
    output_of_updated_lyr, None, updated_fields, QGis.WKBLineString, updated_lyr.crs())


# Buffer both layers
original_buf_layer = buffer(original_lyr, buffer_distance)
updated_buf_layer = buffer(updated_lyr, buffer_distance)


# Find changes in both layers
original_result_ids = find_changes(
    original_lyr, updated_buf_layer, original_id_field,
    updated_id_field, original_writer, original_remain_fields)
updated_result_ids = find_changes(
    updated_lyr, original_buf_layer, updated_id_field,
    original_id_field, updated_writer, updated_remain_fields)

original_lyr = QgsVectorLayer(output_of_original_lyr, "QA Large Changes Original", "ogr")
updated_lyr = QgsVectorLayer(output_of_updated_lyr, "QA Large Changes Updated", "ogr")

del original_writer, updated_writer


# Write changes to files
write_changes_to_output(original_lyr, original_id_field, original_result_ids, updated_result_ids)
write_changes_to_output(updated_lyr, updated_id_field, updated_result_ids, original_result_ids)
