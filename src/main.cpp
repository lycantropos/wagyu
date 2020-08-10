#include <pybind11/functional.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <mapbox/geometry/box.hpp>
#include <mapbox/geometry/multi_polygon.hpp>
#include <mapbox/geometry/point.hpp>
#include <mapbox/geometry/polygon.hpp>
#include <mapbox/geometry/wagyu/bound.hpp>
#include <mapbox/geometry/wagyu/build_local_minima_list.hpp>
#include <mapbox/geometry/wagyu/config.hpp>
#include <mapbox/geometry/wagyu/edge.hpp>
#include <mapbox/geometry/wagyu/local_minimum.hpp>
#include <mapbox/geometry/wagyu/point.hpp>
#include <mapbox/geometry/wagyu/ring.hpp>
#include <mapbox/geometry/wagyu/wagyu.hpp>
#include <sstream>
#include <stdexcept>

namespace py = pybind11;

#define MODULE_NAME _wagyu
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define BOUND_NAME "Bound"
#define BOX_NAME "Box"
#define EDGE_NAME "Edge"
#define EDGE_SIDE_NAME "EdgeSide"
#define FILL_KIND_NAME "FillKind"
#define INTERSECT_NODE_NAME "IntersectNode"
#define LINEAR_RING_NAME "LinearRing"
#define MULTIPOLYGON_NAME "Multipolygon"
#define LOCAL_MINIMUM_NAME "LocalMinimum"
#define LOCAL_MINIMUM_LIST_NAME "LocalMinimumList"
#define OPERATION_KIND_NAME "OperationKind"
#define POINT_NAME "Point"
#define POLYGON_NAME "Polygon"
#define POLYGON_KIND_NAME "PolygonKind"
#define RING_NAME "Ring"
#define RING_MANAGER_NAME "RingManager"
#define WAGYU_NAME "Wagyu"

using coordinate_t = double;
using ActiveBoundList =
    mapbox::geometry::wagyu::active_bound_list<coordinate_t>;
using Box = mapbox::geometry::box<coordinate_t>;
using Bound = mapbox::geometry::wagyu::bound<coordinate_t>;
using BoundPtr = mapbox::geometry::wagyu::bound_ptr<coordinate_t>;
using Edge = mapbox::geometry::wagyu::edge<coordinate_t>;
using EdgeList = mapbox::geometry::wagyu::edge_list<coordinate_t>;
using EdgeSide = mapbox::geometry::wagyu::edge_side;
using FillKind = mapbox::geometry::wagyu::fill_type;
using HotPixelVector = mapbox::geometry::wagyu::hot_pixel_vector<coordinate_t>;
using IntersectList = mapbox::geometry::wagyu::intersect_list<coordinate_t>;
using IntersectNode = mapbox::geometry::wagyu::intersect_node<coordinate_t>;
using LinearRing = mapbox::geometry::linear_ring<coordinate_t>;
using LocalMinimum = mapbox::geometry::wagyu::local_minimum<coordinate_t>;
using LocalMinimumList =
    mapbox::geometry::wagyu::local_minimum_list<coordinate_t>;
using LocalMinimumPtr =
    mapbox::geometry::wagyu::local_minimum_ptr<coordinate_t>;
using LocalMinimumPtrList =
    mapbox::geometry::wagyu::local_minimum_ptr_list<coordinate_t>;
using Multipolygon = mapbox::geometry::multi_polygon<coordinate_t>;
using OperationKind = mapbox::geometry::wagyu::clip_type;
using Point = mapbox::geometry::point<coordinate_t>;
using PointNode = mapbox::geometry::wagyu::point<coordinate_t>;
using Polygon = mapbox::geometry::polygon<coordinate_t>;
using PolygonKind = mapbox::geometry::wagyu::polygon_type;
using Ring = mapbox::geometry::wagyu::ring<coordinate_t>;
using RingPtr = mapbox::geometry::wagyu::ring_ptr<coordinate_t>;
using RingVector = mapbox::geometry::wagyu::ring_vector<coordinate_t>;
using RingManager = mapbox::geometry::wagyu::ring_manager<coordinate_t>;
using ScanbeamList = mapbox::geometry::wagyu::scanbeam_list<coordinate_t>;
using Wagyu = mapbox::geometry::wagyu::wagyu<coordinate_t>;

template <class Iterable>
static py::iterator to_iterator(Iterable& iterable) {
  return py::make_iterator(std::begin(iterable), std::end(iterable));
}

template <class Sequence>
static std::size_t to_size(Sequence& sequence) {
  return sequence.size();
}

template <class Sequence>
static bool contains(const Sequence& sequence,
                     const typename Sequence::value_type& value) {
  return std::find(std::begin(sequence), std::end(sequence), value) !=
         std::end(sequence);
}

template <class Sequence>
static py::list sequence_get_state(const Sequence& sequence) {
  py::list result;
  for (const auto& element : sequence) result.append(element);
  return result;
}

template <class Sequence>
static Sequence sequence_set_state(py::list list) {
  Sequence result;
  for (const auto& element : list)
    result.push_back(element.cast<typename Sequence::value_type>());
  return result;
}

template <class Sequence>
static const typename Sequence::value_type& to_item(const Sequence& sequence,
                                                    std::int64_t index) {
  std::int64_t size = to_size(sequence);
  std::int64_t normalized_index = index >= 0 ? index : index + size;
  if (normalized_index < 0 || normalized_index >= size)
    throw std::out_of_range(std::string("Index should be in range(" +
                                        std::to_string(-size) + ", ") +
                            std::to_string(size > 0 ? size : 1) +
                            "), but found " + std::to_string(index) + ".");
  return sequence[normalized_index];
}

static Point point_node_to_point(const PointNode* node) {
  return Point(node->x, node->y);
}

static std::vector<Point> point_node_to_points(const PointNode* node) {
  std::vector<Point> result;
  if (node == nullptr) return result;
  const auto* cursor = node;
  do {
    result.push_back(point_node_to_point(cursor));
    cursor = cursor->next;
  } while (cursor != node);
  return result;
};

static PointNode* points_to_point_node(RingPtr ring,
                                       const std::vector<Point>& points) {
  if (points.empty()) return nullptr;
  auto iterator = points.rbegin();
  auto result = new PointNode(ring, *(iterator++));
  for (; iterator != points.rend(); ++iterator)
    result = new PointNode(ring, *iterator, result);
  return result;
};

static std::size_t get_bound_current_edge_index(const Bound& self) {
  std::size_t index = self.current_edge - self.edges.begin();
  return std::min(index, self.edges.size());
}

static void set_bound_current_edge_index(Bound& bound, std::size_t value) {
  bound.current_edge =
      bound.edges.begin() + std::min(value, bound.edges.size());
}

static std::size_t get_bound_next_edge_index(const Bound& self) {
  std::size_t index = self.next_edge - self.edges.begin();
  return std::min(index, self.edges.size());
}

static void set_bound_next_edge_index(Bound& bound, std::size_t value) {
  bound.next_edge = bound.edges.begin() + std::min(value, bound.edges.size());
}

static std::size_t get_ring_manager_current_hot_pixel_index(
    const RingManager& manager) {
  std::size_t index = manager.current_hp_itr - manager.hot_pixels.begin();
  return std::min(index, manager.hot_pixels.size());
}

static void set_ring_manager_current_hot_pixel_index(RingManager& manager,
                                                     std::size_t value) {
  manager.current_hp_itr =
      manager.hot_pixels.begin() + std::min(value, manager.hot_pixels.size());
}

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

template <class Object>
std::string repr(const Object& object) {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<double>::digits10 + 2);
  stream << object;
  return stream.str();
}

template <class Object>
static void write_pointer(std::ostream& stream, Object* value) {
  if (value == nullptr)
    stream << py::none();
  else
    stream << *value;
}

template <class Object>
static bool pointers_equal(Object* left, Object* right) {
  return left == nullptr ? right == nullptr
                         : right != nullptr && *left == *right;
}

template <class Sequence>
static bool pointers_sequences_equal(const Sequence& left,
                                     const Sequence& right) {
  if (left.size() != right.size()) return false;
  auto size = to_size(left);
  for (std::size_t index = 0; index < size; ++index)
    if (!pointers_equal(left[index], right[index])) return false;
  return true;
}

template <typename Sequence>
static void write_pointers_sequence(std::ostream& stream,
                                    const Sequence& sequence) {
  stream << "[";
  if (!sequence.empty()) {
    write_pointer(stream, sequence[0]);
    std::for_each(std::next(std::begin(sequence)), std::end(sequence),
                  [&stream](typename Sequence::value_type value) {
                    stream << ", ";
                    write_pointer(stream, value);
                  });
  }
  stream << "]";
};

template <typename Sequence>
static void write_sequence(std::ostream& stream, const Sequence& sequence) {
  stream << "[";
  if (!sequence.empty()) {
    stream << sequence[0];
    std::for_each(std::next(std::begin(sequence)), std::end(sequence),
                  [&stream](const typename Sequence::value_type& value) {
                    stream << ", " << value;
                  });
  }
  stream << "]";
};

namespace mapbox {
namespace geometry {
static std::ostream& operator<<(std::ostream& stream, const Point& point) {
  return stream << C_STR(MODULE_NAME) "." POINT_NAME "(" << point.x << ", "
                << point.y << ")";
}

static std::ostream& operator<<(std::ostream& stream, const LinearRing& ring) {
  stream << C_STR(MODULE_NAME) "." LINEAR_RING_NAME "(";
  write_sequence(stream, ring);
  return stream << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Polygon& polygon) {
  stream << C_STR(MODULE_NAME) "." POLYGON_NAME "(";
  write_sequence(stream, polygon);
  return stream << ")";
}

static std::ostream& operator<<(std::ostream& stream,
                                const Multipolygon& multipolygon) {
  stream << C_STR(MODULE_NAME) "." MULTIPOLYGON_NAME "(";
  write_sequence(stream, multipolygon);
  return stream << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Box& box) {
  return stream << C_STR(MODULE_NAME) "." BOX_NAME "(" << box.min << ", "
                << box.max << ")";
}

namespace wagyu {
static std::ostream& operator<<(std::ostream& stream, const edge_side& side) {
  stream << C_STR(MODULE_NAME) "." EDGE_SIDE_NAME;
  switch (side) {
    case edge_left:
      stream << ".LEFT";
      break;
    case edge_right:
      stream << ".RIGHT";
      break;
  }
  return stream;
}

static std::ostream& operator<<(std::ostream& stream,
                                const polygon_type& type) {
  stream << C_STR(MODULE_NAME) "." POLYGON_KIND_NAME;
  switch (type) {
    case polygon_type_subject:
      stream << ".SUBJECT";
      break;
    case polygon_type_clip:
      stream << ".CLIP";
      break;
  }
  return stream;
}

static std::ostream& operator<<(std::ostream& stream, const Ring& ring) {
  stream << C_STR(MODULE_NAME) "." RING_NAME "(" << ring.ring_index << ", ";
  write_pointers_sequence(stream, ring.children);
  stream << ", ";
  write_sequence(stream, point_node_to_points(ring.points));
  stream << ", " << bool_repr(ring.corrected) << ")";
  return stream;
}

static std::ostream& operator<<(std::ostream& stream,
                                const RingManager& manager) {
  stream << C_STR(MODULE_NAME) "." RING_MANAGER_NAME "(";
  write_pointers_sequence(stream, manager.children);
  stream << ", ";
  write_sequence(stream, manager.hot_pixels);
  stream << ", " << get_ring_manager_current_hot_pixel_index(manager) << ", ";
  write_sequence(stream, manager.rings);
  stream << ", ";
  return stream << manager.index << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Bound& bound) {
  stream << C_STR(MODULE_NAME) "." BOUND_NAME "(";
  write_sequence(stream, bound.edges);
  stream << ", " << get_bound_current_edge_index(bound) << ", "
         << get_bound_next_edge_index(bound) << ", " << bound.last_point
         << ", ";
  write_pointer(stream, bound.ring);
  return stream << ", " << bound.current_x << ", " << bound.pos << ", "
                << bound.winding_count << ", " << bound.winding_count2 << ", "
                << std::to_string(bound.winding_delta) << ", "
                << bound.poly_type << ", " << bound.side << ")";
}

static std::ostream& operator<<(std::ostream& stream,
                                const IntersectNode& node) {
  stream << C_STR(MODULE_NAME) "." INTERSECT_NODE_NAME "(";
  write_pointer(stream, node.bound1);
  stream << ", ";
  write_pointer(stream, node.bound2);
  return stream << ", " << node.pt << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Edge& edge) {
  return stream << C_STR(MODULE_NAME) "." EDGE_NAME "(" << edge.bot << ", "
                << edge.top << ")";
}

static std::ostream& operator<<(std::ostream& stream,
                                const LocalMinimum& minimum) {
  return stream << C_STR(MODULE_NAME) "." LOCAL_MINIMUM_NAME "("
                << minimum.left_bound << ", " << minimum.right_bound << ", "
                << minimum.y << ", "
                << bool_repr(minimum.minimum_has_horizontal) << ")";
}

static std::ostream& operator<<(std::ostream& stream,
                                const LocalMinimumList& list) {
  stream << C_STR(MODULE_NAME) "." LOCAL_MINIMUM_LIST_NAME "(";
  write_sequence(stream, list);
  return stream << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Wagyu& wagyu) {
  stream << C_STR(MODULE_NAME) "." WAGYU_NAME "(";
  write_sequence(stream, wagyu.minima_list);
  stream << ", ";
  return stream << bool_repr(wagyu.reverse_output) << ")";
}

static bool operator==(const Edge& left, const Edge& right) {
  return left.bot == right.bot && left.top == right.top;
}

static bool operator==(const Ring& left, const Ring& right) {
  return left.ring_index == right.ring_index &&
         pointers_sequences_equal(left.children, right.children) &&
         pointers_equal(left.points, right.points) &&
         pointers_equal(left.bottom_point, right.bottom_point) &&
         left.corrected == right.corrected;
}

static bool operator==(const RingManager& left, const RingManager& right) {
  return left.index == right.index &&
         get_ring_manager_current_hot_pixel_index(left) ==
             get_ring_manager_current_hot_pixel_index(right) &&
         pointers_sequences_equal(left.children, right.children) &&
         pointers_sequences_equal(left.all_points, right.all_points) &&
         left.points == right.points && left.hot_pixels == right.hot_pixels &&
         left.rings == right.rings && left.storage == right.storage;
}

static bool operator==(const Bound& self, const Bound& other) {
  return self.edges == other.edges &&
         get_bound_current_edge_index(self) ==
             get_bound_current_edge_index(other) &&
         get_bound_next_edge_index(self) == get_bound_next_edge_index(other) &&
         self.last_point == other.last_point &&
         pointers_equal(self.ring, other.ring) &&
         self.current_x == other.current_x && self.pos == other.pos &&
         self.winding_count == other.winding_count &&
         self.winding_count2 == other.winding_count2 &&
         self.winding_delta == other.winding_delta &&
         self.poly_type == other.poly_type && self.side == other.side;
}

static bool operator==(const IntersectNode& self, const IntersectNode& other) {
  return pointers_equal(self.bound1, other.bound1) &&
         pointers_equal(self.bound2, other.bound2) && self.pt == other.pt;
}

static bool operator==(const LocalMinimum& self, const LocalMinimum& other) {
  return self.left_bound == other.left_bound &&
         self.right_bound == other.right_bound && self.y == other.y &&
         self.minimum_has_horizontal == other.minimum_has_horizontal;
}

static bool operator==(const Wagyu& self, const Wagyu& other) {
  return self.minima_list == other.minima_list &&
         self.reverse_output == other.reverse_output;
}
}  // namespace wagyu
}  // namespace geometry
}  // namespace mapbox

PYBIND11_MAKE_OPAQUE(LocalMinimumList);

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(Python binding of mapbox/wagyu library.)pbdoc";

  py::enum_<OperationKind>(m, OPERATION_KIND_NAME)
      .value("INTERSECTION", OperationKind::clip_type_intersection)
      .value("UNION", OperationKind::clip_type_union)
      .value("DIFFERENCE", OperationKind::clip_type_difference)
      .value("XOR", OperationKind::clip_type_x_or);

  py::enum_<EdgeSide>(m, EDGE_SIDE_NAME)
      .value("LEFT", EdgeSide::edge_left)
      .value("RIGHT", EdgeSide::edge_right);

  py::enum_<FillKind>(m, FILL_KIND_NAME)
      .value("EVEN_ODD", FillKind::fill_type_even_odd)
      .value("NON_ZERO", FillKind::fill_type_non_zero)
      .value("POSITIVE", FillKind::fill_type_positive)
      .value("NEGATIVE", FillKind::fill_type_negative);

  py::enum_<PolygonKind>(m, POLYGON_KIND_NAME)
      .value("SUBJECT", PolygonKind::polygon_type_subject)
      .value("CLIP", PolygonKind::polygon_type_clip);

  py::class_<Point>(m, POINT_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::pickle(
          [](const Point& self) {  // __getstate__
            return py::make_tuple(self.x, self.y);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Point(tuple[0].cast<coordinate_t>(),
                         tuple[1].cast<coordinate_t>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Point>)
      .def_readonly("x", &Point::x)
      .def_readonly("y", &Point::y)
      .def("round", mapbox::geometry::wagyu::round_point<coordinate_t>);

  py::class_<LinearRing>(m, LINEAR_RING_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<Point>&>())
      .def(py::self == py::self)
      .def(py::pickle(&sequence_get_state<LinearRing>,
                      &sequence_set_state<LinearRing>))
      .def("__contains__", contains<LinearRing>)
      .def("__repr__", repr<LinearRing>)
      .def("__len__", to_size<LinearRing>)
      .def("__getitem__", to_item<LinearRing>, py::arg("index"))
      .def("__iter__", to_iterator<LinearRing>, py::keep_alive<0, 1>())
      .def_property_readonly("edges", [](const LinearRing& self) {
        EdgeList result;
        result.reserve(self.size());
        build_edge_list(self, result);
        return result;
      });

  py::class_<Polygon>(m, POLYGON_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<LinearRing>&>())
      .def(py::self == py::self)
      .def(py::pickle(&sequence_get_state<Polygon>,
                      &sequence_set_state<Polygon>))
      .def("__contains__", contains<Polygon>)
      .def("__repr__", repr<Polygon>)
      .def("__len__", to_size<Polygon>)
      .def("__getitem__", to_item<Polygon>, py::arg("index"))
      .def("__iter__", to_iterator<Polygon>, py::keep_alive<0, 1>())
      .def("append",
           mapbox::geometry::wagyu::push_ring_to_polygon<coordinate_t,
                                                         coordinate_t>);

  py::class_<Multipolygon>(m, MULTIPOLYGON_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<Polygon>&>())
      .def(py::self == py::self)
      .def(py::pickle(&sequence_get_state<Multipolygon>,
                      &sequence_set_state<Multipolygon>))
      .def("__contains__", contains<Multipolygon>)
      .def("__repr__", repr<Multipolygon>)
      .def("__len__", to_size<Multipolygon>)
      .def("__getitem__", to_item<Multipolygon>, py::arg("index"))
      .def("__iter__", to_iterator<Multipolygon>, py::keep_alive<0, 1>());

  py::class_<Box>(m, BOX_NAME)
      .def(py::init<Point, Point>(), py::arg("minimum"), py::arg("maximum"))
      .def(py::pickle(
          [](const Box& self) {  // __getstate__
            return py::make_tuple(self.min, self.max);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Box(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Box>)
      .def("inside_of",
           mapbox::geometry::wagyu::box2_contains_box1<coordinate_t>)
      .def_readonly("minimum", &Box::min)
      .def_readonly("maximum", &Box::max);

  py::class_<Edge>(m, EDGE_NAME)
      .def(py::init<Point, Point>(), py::arg("bottom"), py::arg("top"))
      .def(py::pickle(
          [](const Edge& self) {  // __getstate__
            return py::make_tuple(self.bot, self.top);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Edge(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__and__",
           [](const Edge& self, const Edge& other) -> std::unique_ptr<Point> {
             Point intersection;
             if (mapbox::geometry::wagyu::get_edge_intersection(self, other,
                                                                intersection))
               return std::make_unique<Point>(intersection.x, intersection.y);
             else
               return nullptr;
           })
      .def("__repr__", repr<Edge>)
      .def_readonly("bottom", &Edge::bot)
      .def_readonly("top", &Edge::top)
      .def_readonly("slope", &Edge::dx)
      .def_property_readonly(
          "is_horizontal", mapbox::geometry::wagyu::is_horizontal<coordinate_t>)
      .def("get_current_x",
           mapbox::geometry::wagyu::get_current_x<coordinate_t>,
           py::arg("current_y"))
      .def("get_min_x", mapbox::geometry::wagyu::get_edge_min_x<coordinate_t>,
           py::arg("current_y"))
      .def("get_max_x", mapbox::geometry::wagyu::get_edge_max_x<coordinate_t>,
           py::arg("current_y"))
      .def("reverse_horizontal",
           mapbox::geometry::wagyu::reverse_horizontal<coordinate_t>);

  py::class_<Ring, std::unique_ptr<Ring, py::nodelete>>(m, RING_NAME)
      .def(py::init([](std::size_t index, const RingVector& children,
                       const std::vector<Point>& points, bool corrected) {
             auto result = new Ring(index, children, corrected);
             result->points = points_to_point_node(result, points);
             return result;
           }),
           py::arg("index") = 0, py::arg("children") = RingVector{},
           py::arg("points") = std::vector<Point>{},
           py::arg("corrected") = false)
      .def(py::self == py::self)
      .def("__repr__", repr<Ring>)
      .def_readonly("index", &Ring::ring_index)
      .def_readonly("box", &Ring::bbox)
      .def_readonly("parent", &Ring::parent)
      .def_readonly("children", &Ring::children)
      .def_property_readonly(
          "points",
          [](const Ring& self) { return point_node_to_points(self.points); })
      .def_property_readonly("bottom_points",
                             [](const Ring& self) {
                               return point_node_to_points(self.bottom_point);
                             })
      .def_readonly("corrected", &Ring::corrected)
      .def_property_readonly(
          "sorted_points",
          [](RingPtr self) {
            auto nodes =
                mapbox::geometry::wagyu::sort_ring_points<coordinate_t>(self);
            std::vector<Point> result;
            result.reserve(nodes.size());
            for (const auto* node : nodes)
              result.push_back(point_node_to_point(node));
            return result;
          })
      .def_property_readonly("size", &Ring::size)
      .def_property_readonly("area", &Ring::area)
      .def_property_readonly("is_hole", &Ring::is_hole)
      .def_property_readonly("depth",
                             mapbox::geometry::wagyu::ring_depth<coordinate_t>)
      .def("inside_of",
           mapbox::geometry::wagyu::poly2_contains_poly1<coordinate_t>)
      .def("is_descendant_of",
           mapbox::geometry::wagyu::ring1_child_below_ring2<coordinate_t>)
      .def("recalculate_stats", &Ring::recalculate_stats)
      .def("reset_stats", &Ring::reset_stats)
      .def("set_stats", &Ring::set_stats, py::arg("area"), py::arg("size"),
           py::arg("box"))
      .def("update_points",
           mapbox::geometry::wagyu::update_points_ring<coordinate_t>);

  py::class_<Bound, std::unique_ptr<Bound, py::nodelete>>(m, BOUND_NAME)
      .def(py::init([](const EdgeList& edges, std::size_t current_edge_index,
                       std::size_t next_edge_index, const Point& last_point,
                       RingPtr ring, double current_x, std::size_t position,
                       std::int32_t winding_count,
                       std::int32_t opposite_winding_count,
                       std::int8_t winding_delta, PolygonKind polygon_kind,
                       EdgeSide edge_side) {
             auto result = Bound(edges, last_point, ring, current_x, position,
                                 winding_count, opposite_winding_count,
                                 winding_delta, polygon_kind, edge_side);
             set_bound_current_edge_index(result, current_edge_index);
             set_bound_next_edge_index(result, next_edge_index);
             return result;
           }),
           py::arg("edges") = EdgeList{},
           py::arg("current_edge_index") =
               std::numeric_limits<std::size_t>::max(),
           py::arg("next_edge_index") = std::numeric_limits<std::size_t>::max(),
           py::arg("last_point") = Point{0, 0},
           py::arg("ring").none(true) = nullptr, py::arg("current_x") = 0.,
           py::arg("position") = 0, py::arg("winding_count") = 0,
           py::arg("opposite_winding_count") = 0, py::arg("winding_delta") = 0,
           py::arg("polygon_kind") = PolygonKind::polygon_type_subject,
           py::arg("side") = mapbox::geometry::wagyu::edge_left)
      .def(py::self == py::self)
      .def("__repr__", repr<Bound>)
      .def_readonly("edges", &Bound::edges)
      .def_readonly("last_point", &Bound::last_point)
      .def_readonly("ring", &Bound::ring)
      .def_readonly("maximum_bound", &Bound::maximum_bound)
      .def_readonly("current_x", &Bound::current_x)
      .def_readonly("position", &Bound::pos)
      .def_readonly("winding_count", &Bound::winding_count)
      .def_readonly("opposite_winding_count", &Bound::winding_count2)
      .def_readonly("winding_delta", &Bound::winding_delta)
      .def_readonly("polygon_kind", &Bound::poly_type)
      .def_readonly("side", &Bound::side)
      .def_property("current_edge_index", get_bound_current_edge_index,
                    set_bound_current_edge_index)
      .def_property("next_edge_index", get_bound_next_edge_index,
                    set_bound_next_edge_index)
      .def_property_readonly(
          "current_edge",
          [](const Bound& self) {
            if (static_cast<std::size_t>(self.current_edge -
                                         self.edges.begin()) >=
                self.edges.size())
              throw std::out_of_range("list index out of range");
            return *self.current_edge;
          })
      .def_property_readonly(
          "next_edge",
          [](const Bound& self) {
            if (static_cast<std::size_t>(self.next_edge - self.edges.begin()) >=
                self.edges.size())
              throw std::out_of_range("list index out of range");
            return *self.next_edge;
          })
      .def("is_contributing",
           mapbox::geometry::wagyu::is_contributing<coordinate_t>)
      .def("is_even_odd_fill_kind",
           mapbox::geometry::wagyu::is_even_odd_fill_type<coordinate_t>)
      .def("is_even_odd_alt_fill_kind",
           mapbox::geometry::wagyu::is_even_odd_alt_fill_type<coordinate_t>)
      .def("is_intermediate",
           [](const Bound& self, coordinate_t y) {
             return mapbox::geometry::wagyu::is_intermediate<coordinate_t>(self,
                                                                           y);
           })
      .def("is_maxima",
           [](const Bound& self, coordinate_t y) {
             return mapbox::geometry::wagyu::is_maxima<coordinate_t>(self, y);
           })
      .def("fix_horizontals",
           mapbox::geometry::wagyu::fix_horizontals<coordinate_t>)
      .def("move_horizontals",
           mapbox::geometry::wagyu::move_horizontals_on_left_to_right<
               coordinate_t>)
      .def("to_next_edge", [](Bound& self, ScanbeamList& scanbeams) {
        mapbox::geometry::wagyu::next_edge_in_bound(self, scanbeams);
        return scanbeams;
      });

  py::class_<IntersectNode>(m, INTERSECT_NODE_NAME)
      .def(py::init<const BoundPtr&, const BoundPtr&, const Point&>(),
           py::arg("first_bound"), py::arg("second_bound"), py::arg("point"))
      .def(py::self == py::self)
      .def("__lt__",
           [](const IntersectNode& self, const IntersectNode& other) {
             static mapbox::geometry::wagyu::intersect_list_sorter<coordinate_t>
                 sorter;
             return sorter(self, other);
           })
      .def("__repr__", repr<IntersectNode>)
      .def_readonly("first_bound", &IntersectNode::bound1)
      .def_readonly("second_bound", &IntersectNode::bound2)
      .def_readonly("point", &IntersectNode::pt);

  py::class_<LocalMinimum>(m, LOCAL_MINIMUM_NAME)
      .def(py::init([](const Bound& left_bound, const Bound& right_bound,
                       coordinate_t y, bool minimum_has_horizontal) {
        return std::make_unique<LocalMinimum>(
            Bound(left_bound), Bound(right_bound), y, minimum_has_horizontal);
      }))
      .def(py::self == py::self)
      .def("__repr__", repr<LocalMinimum>)
      .def("__lt__",
           [](LocalMinimumPtr self, LocalMinimumPtr other) {
             static mapbox::geometry::wagyu::local_minimum_sorter<coordinate_t>
                 sorter;
             return sorter(other, self);
           })
      .def_readonly("left_bound", &LocalMinimum::left_bound)
      .def_readonly("right_bound", &LocalMinimum::right_bound)
      .def_readonly("y", &LocalMinimum::y)
      .def_readonly("minimum_has_horizontal",
                    &LocalMinimum::minimum_has_horizontal);

  py::class_<LocalMinimumList>(m, LOCAL_MINIMUM_LIST_NAME)
      .def(py::init<>())
      .def(py::init([](const std::vector<LocalMinimum>& minimums) {
        return LocalMinimumList(minimums.begin(), minimums.end());
      }))
      .def(py::self == py::self)
      .def("__repr__", repr<LocalMinimumList>)
      .def("__contains__", contains<LocalMinimumList>)
      .def("__len__", to_size<LocalMinimumList>)
      .def("__getitem__", to_item<LocalMinimumList>, py::arg("index"),
           py::return_value_policy::reference)
      .def("__iter__", to_iterator<LocalMinimumList>, py::keep_alive<0, 1>())
      .def("add_linear_ring",
           [](LocalMinimumList& self, const LinearRing& ring,
              PolygonKind polygon_kind) {
             return mapbox::geometry::wagyu::add_linear_ring(ring, self,
                                                             polygon_kind);
           })
      .def_property_readonly("scanbeams", [](LocalMinimumList& self) {
        ScanbeamList result;
        mapbox::geometry::wagyu::setup_scanbeam<coordinate_t>(self, result);
        return result;
      });

  py::class_<Wagyu>(m, WAGYU_NAME)
      .def(py::init<>([](bool reverse_output) {
             auto result = std::make_unique<Wagyu>();
             result->reverse_rings(reverse_output);
             return result;
           }),
           py::arg("reverse_output") = false)
      .def(py::self == py::self)
      .def("__repr__", repr<Wagyu>)
      .def("add_linear_ring", &Wagyu::add_ring<coordinate_t>)
      .def("add_polygon", &Wagyu::add_polygon<coordinate_t>)
      .def("clear", &Wagyu::clear)
      .def(
          "intersect",
          [](Wagyu& self,
             FillKind subject_fill_kind = FillKind::fill_type_even_odd,
             FillKind clip_fill_kind = FillKind::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(OperationKind::clip_type_intersection, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") = FillKind::fill_type_even_odd,
          py::arg("clip_fill_kind") = FillKind::fill_type_even_odd)
      .def(
          "subtract",
          [](Wagyu& self,
             FillKind subject_fill_kind = FillKind::fill_type_even_odd,
             FillKind clip_fill_kind = FillKind::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(OperationKind::clip_type_difference, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") = FillKind::fill_type_even_odd,
          py::arg("clip_fill_kind") = FillKind::fill_type_even_odd)
      .def(
          "unite",
          [](Wagyu& self,
             FillKind subject_fill_kind = FillKind::fill_type_even_odd,
             FillKind clip_fill_kind = FillKind::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(OperationKind::clip_type_union, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") = FillKind::fill_type_even_odd,
          py::arg("clip_fill_kind") = FillKind::fill_type_even_odd)
      .def(
          "symmetric_subtract",
          [](Wagyu& self,
             FillKind subject_fill_kind = FillKind::fill_type_even_odd,
             FillKind clip_fill_kind = FillKind::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(OperationKind::clip_type_x_or, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") = FillKind::fill_type_even_odd,
          py::arg("clip_fill_kind") = FillKind::fill_type_even_odd)
      .def_property_readonly("bounds", &Wagyu::get_bounds)
      .def_readonly("minimums", &Wagyu::minima_list)
      .def_readonly("reverse_output", &Wagyu::reverse_output);

  py::class_<RingManager>(m, RING_MANAGER_NAME)
      .def(
          py::init([](const RingVector& children,
                      const HotPixelVector& hot_pixels,
                      std::size_t current_hot_pixel_index,
                      const std::deque<Ring>& rings, std::size_t index) {
            auto result = std::make_unique<RingManager>(children, hot_pixels,
                                                        rings, index);
            for (auto* ring : result->children)
              if (ring != nullptr && ring->points != nullptr)
                mapbox::geometry::wagyu::update_points_ring<coordinate_t>(ring);
            for (auto& ring : result->rings)
              if (ring.points != nullptr)
                mapbox::geometry::wagyu::update_points_ring<coordinate_t>(
                    &ring);
            set_ring_manager_current_hot_pixel_index(*result,
                                                     current_hot_pixel_index);
            return result;
          }),
          py::arg("children") = RingVector{},
          py::arg("hot_pixels") = HotPixelVector{},
          py::arg("current_hot_pixel_index") =
              std::numeric_limits<std::size_t>::max(),
          py::arg("rings") = std::deque<Ring>{}, py::arg("index") = 0)
      .def(py::self == py::self)
      .def("__repr__", repr<RingManager>)
      .def_readonly("children", &RingManager::children)
      .def_readonly("hot_pixels", &RingManager::hot_pixels)
      .def_property("current_hot_pixel_index",
                    get_ring_manager_current_hot_pixel_index,
                    set_ring_manager_current_hot_pixel_index)
      .def_property_readonly("all_points",
                             [](const RingManager& self) {
                               std::vector<std::vector<Point>> result;
                               for (const auto* node : self.all_points)
                                 result.push_back(point_node_to_points(node));
                               return result;
                             })
      .def_property_readonly("points",
                             [](const RingManager& self) {
                               std::vector<std::vector<Point>> result;
                               for (const auto& node : self.points)
                                 result.push_back(point_node_to_points(&node));
                               return result;
                             })
      .def_readonly("rings", &RingManager::rings)
      .def_property_readonly("stored_points",
                             [](const RingManager& self) {
                               std::vector<std::vector<Point>> result;
                               for (const auto& node : self.storage)
                                 result.push_back(point_node_to_points(&node));
                               return result;
                             })
      .def_property_readonly(
          "sorted_rings",
          mapbox::geometry::wagyu::sort_rings_smallest_to_largest<coordinate_t>)
      .def_readonly("index", &RingManager::index)
      .def("add_first_point",
           [](RingManager& self, std::size_t bound_index,
              ActiveBoundList& active_bounds, const Point& point) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             mapbox::geometry::wagyu::add_first_point<coordinate_t>(
                 *active_bounds[bound_index], active_bounds, point, self);
             return active_bounds;
           })
      .def("add_point",
           [](RingManager& self, std::size_t bound_index,
              ActiveBoundList& active_bounds, const Point& point) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             mapbox::geometry::wagyu::add_point<coordinate_t>(
                 *active_bounds[bound_index], active_bounds, point, self);
             return active_bounds;
           })
      .def("add_point_to_ring",
           [](RingManager& self, Bound& bound, const Point& point) {
             mapbox::geometry::wagyu::add_point_to_ring<coordinate_t>(
                 bound, point, self);
           })
      .def("append_ring",
           [](RingManager& self, std::size_t first_bound_index,
              std::size_t second_bound_index, ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::append_ring<coordinate_t>(
                 *active_bounds[first_bound_index],
                 *active_bounds[second_bound_index], active_bounds, self);
             return active_bounds;
           })
      .def("add_local_maximum_point",
           [](RingManager& self, const Point& point,
              std::size_t first_bound_index, std::size_t second_bound_index,
              ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::add_local_maximum_point<coordinate_t>(
                 *active_bounds[first_bound_index],
                 *active_bounds[second_bound_index], point, self,
                 active_bounds);
             return active_bounds;
           })
      .def("add_local_minimum_point",
           [](RingManager& self, const Point& point,
              std::size_t first_bound_index, std::size_t second_bound_index,
              ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::add_local_minimum_point<coordinate_t>(
                 *active_bounds[first_bound_index],
                 *active_bounds[second_bound_index], active_bounds, point,
                 self);
             return active_bounds;
           })
      .def("execute_vatti",
           [](RingManager& self, LocalMinimumList& minimums,
              OperationKind operation_kind, FillKind subject_fill_kind,
              FillKind clip_fill_kind) {
             mapbox::geometry::wagyu::execute_vatti<coordinate_t>(
                 minimums, self, operation_kind, subject_fill_kind,
                 clip_fill_kind);
           })
      .def("intersect_bounds",
           [](RingManager& self, const Point& point,
              OperationKind operation_kind, FillKind subject_fill_type,
              FillKind clip_fill_type, std::size_t first_bound_index,
              std::size_t second_bound_index, ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::intersect_bounds<coordinate_t>(
                 *active_bounds[first_bound_index],
                 *active_bounds[second_bound_index], point, operation_kind,
                 subject_fill_type, clip_fill_type, self, active_bounds);
             return active_bounds;
           })
      .def("build_hot_pixels",
           [](RingManager& self, LocalMinimumList& minimums) {
             mapbox::geometry::wagyu::build_hot_pixels<coordinate_t>(minimums,
                                                                     self);
           })
      .def("build_result",
           [](RingManager const& self, bool reverse_output) {
             auto* result = new Multipolygon{};
             mapbox::geometry::wagyu::build_result<coordinate_t>(
                 *result, self, reverse_output);
             return result;
           })
      .def(
          "insert_local_minima_into_abl",
          [](RingManager& self, OperationKind operation_kind,
             FillKind subject_fill_kind, FillKind clip_fill_kind,
             coordinate_t bot_y, ScanbeamList& scanbeams,
             LocalMinimumList& minimums, std::size_t minimums_index,
             ActiveBoundList& active_bounds) {
            LocalMinimumPtrList minimums_ptr;
            for (auto& minimum : minimums) minimums_ptr.push_back(&minimum);
            auto minimums_itr = minimums_ptr.begin() + minimums_index;
            mapbox::geometry::wagyu::insert_local_minima_into_ABL<coordinate_t>(
                bot_y, minimums_ptr, minimums_itr, active_bounds, self,
                scanbeams, operation_kind, subject_fill_kind, clip_fill_kind);
            return py::make_tuple(active_bounds, scanbeams,
                                  minimums_itr - minimums_ptr.begin());
          })
      .def("correct_chained_rings",
           mapbox::geometry::wagyu::correct_chained_rings<coordinate_t>)
      .def("correct_collinear_edges",
           mapbox::geometry::wagyu::correct_collinear_edges<coordinate_t>)
      .def("correct_orientations",
           mapbox::geometry::wagyu::correct_orientations<coordinate_t>)
      .def("correct_self_intersections",
           mapbox::geometry::wagyu::correct_self_intersections<coordinate_t>)
      .def("correct_topology",
           mapbox::geometry::wagyu::correct_topology<coordinate_t>)
      .def("correct_tree", mapbox::geometry::wagyu::correct_tree<coordinate_t>)
      .def("insert_horizontal_local_minima_into_abl",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              coordinate_t bot_y, ScanbeamList& scanbeams,
              LocalMinimumList& minimums, std::size_t minimums_index,
              ActiveBoundList& active_bounds) {
             LocalMinimumPtrList minimums_ptr;
             for (auto& minimum : minimums) minimums_ptr.push_back(&minimum);
             auto minimums_itr = minimums_ptr.begin() + minimums_index;
             mapbox::geometry::wagyu::insert_horizontal_local_minima_into_ABL<
                 coordinate_t>(bot_y, minimums_ptr, minimums_itr, active_bounds,
                               self, scanbeams, operation_kind,
                               subject_fill_kind, clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams,
                                   minimums_itr - minimums_ptr.begin());
           })
      .def("insert_local_minima_into_abl_hot_pixel",
           [](RingManager& self, coordinate_t top_y, LocalMinimumList& minimums,
              std::size_t minimums_index, ActiveBoundList& active_bounds,
              ScanbeamList& scanbeams) {
             LocalMinimumPtrList minimums_ptr;
             for (auto& minimum : minimums) minimums_ptr.push_back(&minimum);
             auto minimums_itr = minimums_ptr.begin() + minimums_index;
             mapbox::geometry::wagyu::insert_local_minima_into_ABL_hot_pixel<
                 coordinate_t>(top_y, minimums_ptr, minimums_itr, active_bounds,
                               self, scanbeams);
             return py::make_tuple(active_bounds, scanbeams,
                                   minimums_itr - minimums_ptr.begin());
           })
      .def("horizontals_at_top_scanbeam",
           [](RingManager& self, coordinate_t top_y,
              ActiveBoundList& active_bounds, std::size_t current_bound_index) {
             auto current_bound = active_bounds.begin() + current_bound_index;
             bool shifted =
                 mapbox::geometry::wagyu::horizontals_at_top_scanbeam<
                     coordinate_t>(top_y, current_bound, active_bounds, self);
             return py::make_tuple(
                 active_bounds, current_bound - active_bounds.begin(), shifted);
           })
      .def("do_maxima",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              std::size_t bound_index, std::size_t bound_maximum_index,
              ActiveBoundList& active_bounds) {
             auto bound_iterator = active_bounds.begin() + bound_index;
             auto bound_maximum_iterator =
                 active_bounds.begin() + bound_maximum_index;
             auto itr = mapbox::geometry::wagyu::do_maxima(
                 bound_iterator, bound_maximum_iterator, operation_kind,
                 subject_fill_kind, clip_fill_kind, self, active_bounds);
             return py::make_tuple(active_bounds, itr - active_bounds.begin());
           })
      .def("process_edges_at_top_of_scanbeam",
           [](RingManager& self, coordinate_t top_y, ScanbeamList& scanbeams,
              OperationKind operation_kind, FillKind subject_fill_kind,
              FillKind clip_fill_kind, ActiveBoundList& active_bounds,
              LocalMinimumList& minimums, std::size_t minimums_index) {
             LocalMinimumPtrList minimums_ptr;
             for (auto& minimum : minimums) minimums_ptr.push_back(&minimum);
             auto minimums_itr = minimums_ptr.begin() + minimums_index;
             mapbox::geometry::wagyu::process_edges_at_top_of_scanbeam<
                 coordinate_t>(top_y, active_bounds, scanbeams, minimums_ptr,
                               minimums_itr, self, operation_kind,
                               subject_fill_kind, clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams,
                                   minimums_itr - minimums_ptr.begin());
           })
      .def("process_horizontals",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              coordinate_t scanline_y, ScanbeamList& scanbeams,
              ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::process_horizontals<coordinate_t>(
                 scanline_y, active_bounds, self, scanbeams, operation_kind,
                 subject_fill_kind, clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams);
           })
      .def("process_horizontal",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              coordinate_t scanline_y, ScanbeamList& scanbeams,
              std::size_t bound_index, ActiveBoundList& active_bounds) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             auto bounds_itr = active_bounds.begin() + bound_index;
             auto result =
                 mapbox::geometry::wagyu::process_horizontal<coordinate_t>(
                     scanline_y, bounds_itr, active_bounds, self, scanbeams,
                     operation_kind, subject_fill_kind, clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams,
                                   result - active_bounds.begin());
           })
      .def("process_horizontal_left_to_right",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              coordinate_t scanline_y, ScanbeamList& scanbeams,
              std::size_t bound_index, ActiveBoundList& active_bounds) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             auto bounds_itr = active_bounds.begin() + bound_index;
             auto result =
                 mapbox::geometry::wagyu::process_horizontal_left_to_right<
                     coordinate_t>(scanline_y, bounds_itr, active_bounds, self,
                                   scanbeams, operation_kind, subject_fill_kind,
                                   clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams,
                                   result - active_bounds.begin());
           })
      .def("process_horizontal_right_to_left",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              coordinate_t scanline_y, ScanbeamList& scanbeams,
              std::size_t bound_index, ActiveBoundList& active_bounds) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             auto bounds_itr = active_bounds.begin() + bound_index;
             auto result =
                 mapbox::geometry::wagyu::process_horizontal_right_to_left<
                     coordinate_t>(scanline_y, bounds_itr, active_bounds, self,
                                   scanbeams, operation_kind, subject_fill_kind,
                                   clip_fill_kind);
             return py::make_tuple(active_bounds, scanbeams,
                                   result - active_bounds.begin());
           })
      .def(
          "process_hot_pixel_edges_at_top_of_scanbeam",
          [](RingManager& self, coordinate_t top_y, ScanbeamList& scanbeams,
             ActiveBoundList& active_bounds) {
            mapbox::geometry::wagyu::process_hot_pixel_edges_at_top_of_scanbeam(
                top_y, scanbeams, active_bounds, self);
            return py::make_tuple(active_bounds, scanbeams);
          })
      .def("process_hot_pixel_intersections",
           [](RingManager& self, coordinate_t top_y,
              ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::process_hot_pixel_intersections<
                 coordinate_t>(top_y, active_bounds, self);
             return active_bounds;
           })
      .def("process_intersections",
           [](RingManager& self, coordinate_t top_y,
              OperationKind operation_kind, FillKind subject_fill_kind,
              FillKind clip_fill_kind, ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::process_intersections<coordinate_t>(
                 top_y, active_bounds, operation_kind, subject_fill_kind,
                 clip_fill_kind, self);
             return active_bounds;
           })
      .def("set_hole_state",
           [](RingManager& self, std::size_t bound_index,
              const ActiveBoundList& active_bounds) {
             if (bound_index >= active_bounds.size())
               throw std::out_of_range("list index out of range");
             mapbox::geometry::wagyu::set_hole_state<coordinate_t>(
                 *active_bounds[bound_index], active_bounds, self);
             return active_bounds;
           })
      .def("hot_pixel_set_left_to_right",
           [](RingManager& self, coordinate_t y, coordinate_t start_x,
              coordinate_t end_x, Bound& bound, std::size_t hot_pixel_start,
              std::size_t hot_pixel_stop, bool add_end_point) {
             auto hot_pixels_start_iterator =
                 self.hot_pixels.begin() + hot_pixel_start;
             auto hot_pixels_stop_iterator =
                 self.hot_pixels.begin() + hot_pixel_stop;
             mapbox::geometry::wagyu::hot_pixel_set_left_to_right<coordinate_t>(
                 y, start_x, end_x, bound, self, hot_pixels_start_iterator,
                 hot_pixels_stop_iterator, add_end_point);
             return hot_pixels_start_iterator - self.hot_pixels.begin();
           })
      .def("hot_pixel_set_right_to_left",
           [](RingManager& self, coordinate_t y, coordinate_t start_x,
              coordinate_t end_x, Bound& bound, std::size_t hot_pixel_start,
              std::size_t hot_pixel_stop, bool add_end_point) {
             auto hot_pixels_start_iterator =
                 self.hot_pixels.rend() - hot_pixel_stop;
             auto hot_pixels_stop_iterator =
                 self.hot_pixels.rend() - hot_pixel_start;
             mapbox::geometry::wagyu::hot_pixel_set_right_to_left<coordinate_t>(
                 y, start_x, end_x, bound, self, hot_pixels_start_iterator,
                 hot_pixels_stop_iterator, add_end_point);
             return hot_pixels_start_iterator.base() - self.hot_pixels.begin() -
                    1;
           })
      .def("insert_hot_pixels_in_path",
           [](RingManager& self, Bound& bound, const Point& end_point,
              bool add_end_point) {
             mapbox::geometry::wagyu::insert_hot_pixels_in_path<coordinate_t>(
                 bound, end_point, self, add_end_point);
           })
      .def("insert_lm_left_and_right_bound",
           [](RingManager& self, OperationKind operation_kind,
              FillKind subject_fill_kind, FillKind clip_fill_kind,
              ScanbeamList& scanbeams, std::size_t left_bound_index,
              std::size_t right_bound_index, ActiveBoundList& active_bounds) {
             mapbox::geometry::wagyu::insert_lm_left_and_right_bound<
                 coordinate_t>(*active_bounds[left_bound_index],
                               *active_bounds[right_bound_index], active_bounds,
                               self, scanbeams, operation_kind,
                               subject_fill_kind, clip_fill_kind);
             return py::make_tuple(scanbeams, active_bounds);
           })
      .def("create_ring",
           mapbox::geometry::wagyu::create_new_ring<coordinate_t>)
      .def(
          "assign_as_child",
          [](RingManager& self, RingPtr ring, RingPtr parent) {
            mapbox::geometry::wagyu::assign_as_child<coordinate_t>(ring, parent,
                                                                   self);
          },
          py::arg("ring").none(false), py::arg("parent").none(true))
      .def(
          "reassign_as_child",
          [](RingManager& self, RingPtr ring, RingPtr parent) {
            mapbox::geometry::wagyu::reassign_as_child<coordinate_t>(
                ring, parent, self);
          },
          py::arg("ring").none(false), py::arg("parent").none(true))
      .def(
          "assign_as_sibling",
          [](RingManager& self, RingPtr ring, RingPtr sibling) {
            mapbox::geometry::wagyu::assign_as_sibling<coordinate_t>(
                ring, sibling, self);
          },
          py::arg("ring").none(false), py::arg("sibling").none(false))
      .def(
          "reassign_as_sibling",
          [](RingManager& self, RingPtr ring, RingPtr sibling) {
            mapbox::geometry::wagyu::reassign_as_sibling<coordinate_t>(
                ring, sibling, self);
          },
          py::arg("ring").none(false), py::arg("sibling").none(false))
      .def(
          "replace_ring",
          [](RingManager& self, RingPtr original, RingPtr replacement) {
            mapbox::geometry::wagyu::ring1_replaces_ring2<coordinate_t>(
                replacement, original, self);
          },
          py::arg("original").none(true), py::arg("replacement").none(false))
      .def(
          "remove_ring_and_points",
          [](RingManager& self, RingPtr ring, bool remove_children = true,
             bool remove_from_parent = true) {
            mapbox::geometry::wagyu::remove_ring_and_points<coordinate_t>(
                ring, self, remove_children, remove_from_parent);
          },
          py::arg("ring").none(false), py::arg("remove_children") = true,
          py::arg("remove_from_parent") = true)
      .def(
          "remove_ring",
          [](RingManager& self, RingPtr ring, bool remove_children = true,
             bool remove_from_parent = true) {
            mapbox::geometry::wagyu::remove_ring<coordinate_t>(
                ring, self, remove_children, remove_from_parent);
          },
          py::arg("ring").none(false), py::arg("remove_children") = true,
          py::arg("remove_from_parent") = true)
      .def("sort_hot_pixels",
           mapbox::geometry::wagyu::sort_hot_pixels<coordinate_t>);

  m.def("bound_insert_location", [](const Bound& self, const BoundPtr& other) {
    const auto comparator =
        mapbox::geometry::wagyu::bound_insert_location<coordinate_t>(self);
    return comparator(other);
  });

  m.def("insert_bound_into_abl",
        [](Bound& left, Bound& right, ActiveBoundList& active_bounds) {
          auto result = mapbox::geometry::wagyu::insert_bound_into_ABL(
              left, right, active_bounds);
          return py::make_tuple(active_bounds, result - active_bounds.begin());
        });

  m.def("are_points_slopes_equal", [](const Point& pt1, const Point& pt2,
                                      const Point& pt3) {
    return mapbox::geometry::wagyu::slopes_equal<coordinate_t>(pt1, pt2, pt3);
  });

  m.def("are_edges_slopes_equal", [](const Edge& e1, const Edge& e2) {
    return mapbox::geometry::wagyu::slopes_equal<coordinate_t>(e1, e2);
  });

  m.def("are_floats_almost_equal", mapbox::geometry::wagyu::values_are_equal);

  m.def("bubble_sort",
        [](std::vector<py::object> sequence,
           std::function<bool(py::object, py::object)> comparator,
           std::function<void(py::object, py::object)> on_swap) {
          mapbox::geometry::wagyu::bubble_sort(sequence.begin(), sequence.end(),
                                               comparator, on_swap);
          return sequence;
        });

  m.def("build_intersect_list", [](ActiveBoundList& active_bounds) {
    IntersectList intersections;
    mapbox::geometry::wagyu::build_intersect_list(active_bounds, intersections);
    return py::make_tuple(active_bounds, intersections);
  });

  m.def("is_point_between_others",
        mapbox::geometry::wagyu::point_2_is_between_point_1_and_point_3<
            coordinate_t>);

  m.def("create_bound_towards_maximum",
        mapbox::geometry::wagyu::create_bound_towards_maximum<coordinate_t>);

  m.def("create_bound_towards_minimum",
        mapbox::geometry::wagyu::create_bound_towards_minimum<coordinate_t>);

  m.def("round_towards_min",
        mapbox::geometry::wagyu::round_towards_min<coordinate_t>);

  m.def("round_towards_max",
        mapbox::geometry::wagyu::round_towards_max<coordinate_t>);

  m.def("set_winding_count",
        [](std::size_t bound_index, ActiveBoundList& active_bounds,
           FillKind subject_fill_kind, FillKind clip_fill_kind) {
          mapbox::geometry::wagyu::set_winding_count<coordinate_t>(
              active_bounds.begin() + bound_index, active_bounds,
              subject_fill_kind, clip_fill_kind);
          return active_bounds;
        });

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
