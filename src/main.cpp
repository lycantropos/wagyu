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
#define LINEAR_RING_NAME "LinearRing"
#define MULTIPOLYGON_NAME "Multipolygon"
#define LOCAL_MINIMUM_NAME "LocalMinimum"
#define LOCAL_MINIMUM_LIST_NAME "LocalMinimumList"
#define OPERATION_KIND_NAME "OperationKind"
#define POINT_NAME "Point"
#define POINT_NODE_NAME "PointNode"
#define POLYGON_NAME "Polygon"
#define POLYGON_KIND_NAME "PolygonKind"
#define RING_NAME "Ring"
#define RING_MANAGER_NAME "RingManager"
#define WAGYU_NAME "Wagyu"

using coordinate_t = double;
using Box = mapbox::geometry::box<coordinate_t>;
using Bound = mapbox::geometry::wagyu::bound<coordinate_t>;
using Edge = mapbox::geometry::wagyu::edge<coordinate_t>;
using LinearRing = mapbox::geometry::linear_ring<coordinate_t>;
using LocalMinimum = mapbox::geometry::wagyu::local_minimum<coordinate_t>;
using LocalMinimumList =
    mapbox::geometry::wagyu::local_minimum_list<coordinate_t>;
using Multipolygon = mapbox::geometry::multi_polygon<coordinate_t>;
using Point = mapbox::geometry::point<coordinate_t>;
using PointNode = mapbox::geometry::wagyu::point<coordinate_t>;
using PointNodePtr = mapbox::geometry::wagyu::point_ptr<coordinate_t>;
using Polygon = mapbox::geometry::polygon<coordinate_t>;
using Ring = mapbox::geometry::wagyu::ring<coordinate_t>;
using RingPtr = mapbox::geometry::wagyu::ring_ptr<coordinate_t>;
using RingVector = mapbox::geometry::wagyu::ring_vector<coordinate_t>;
using RingManager = mapbox::geometry::wagyu::ring_manager<coordinate_t>;
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
static const typename Sequence::value_type& to_item(const Sequence& self,
                                                    std::int64_t index) {
  std::int64_t size = to_size(self);
  std::int64_t normalized_index = index >= 0 ? index : index + size;
  if (normalized_index < 0 || normalized_index >= size)
    throw std::out_of_range(std::string("Index should be in range(" +
                                        std::to_string(-size) + ", ") +
                            std::to_string(size > 0 ? size : 1) +
                            "), but found " + std::to_string(index) + ".");
  return self[normalized_index];
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
static std::ostream& operator<<(std::ostream& stream, const clip_type& type) {
  stream << C_STR(MODULE_NAME) "." OPERATION_KIND_NAME;
  switch (type) {
    case clip_type_intersection:
      stream << ".INTERSECTION";
      break;
    case clip_type_union:
      stream << ".UNION";
      break;
    case clip_type_difference:
      stream << ".DIFFERENCE";
      break;
    case clip_type_x_or:
      stream << ".XOR";
      break;
  }
  return stream;
}

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

static std::ostream& operator<<(std::ostream& stream, const fill_type& type) {
  stream << C_STR(MODULE_NAME) "." FILL_KIND_NAME;
  switch (type) {
    case fill_type_even_odd:
      stream << ".EVEN_ODD";
      break;
    case fill_type_non_zero:
      stream << ".NON_ZERO";
      break;
    case fill_type_positive:
      stream << ".POSITIVE";
      break;
    case fill_type_negative:
      stream << ".NEGATIVE";
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

static std::ostream& operator<<(std::ostream& stream, const PointNode& point) {
  return stream << C_STR(MODULE_NAME) "." POINT_NODE_NAME "(" << point.x << ", "
                << point.y << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Ring& ring) {
  stream << C_STR(MODULE_NAME) "." RING_NAME "(" << ring.ring_index << ", ";
  write_pointers_sequence(stream, ring.children);
  stream << ", ";
  write_pointer(stream, ring.points);
  stream << ", ";
  write_pointer(stream, ring.bottom_point);
  stream << ", " << bool_repr(ring.corrected) << ")";
  return stream;
}

static std::ostream& operator<<(std::ostream& stream,
                                const RingManager& manager) {
  return stream << C_STR(MODULE_NAME) "." RING_MANAGER_NAME "()";
}

static std::ostream& operator<<(std::ostream& stream, const Bound& bound) {
  stream << C_STR(MODULE_NAME) "." BOUND_NAME "(";
  write_sequence(stream, bound.edges);
  stream << ", " << bound.last_point << ", ";
  write_pointer(stream, bound.ring);
  return stream << ", " << bound.current_x << ", " << bound.pos << ", "
                << bound.winding_count << ", " << bound.winding_count2 << ", "
                << std::to_string(bound.winding_delta) << ", "
                << bound.poly_type << ", " << bound.side << ")";
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

static bool operator==(const Bound& self, const Bound& other) {
  return self.edges == other.edges && self.last_point == other.last_point &&
         pointers_equal(self.ring, other.ring) &&
         self.current_x == other.current_x && self.pos == other.pos &&
         self.winding_count == other.winding_count &&
         self.winding_count2 == other.winding_count2 &&
         self.winding_delta == other.winding_delta &&
         self.poly_type == other.poly_type && self.side == other.side;
}

static bool operator==(const LocalMinimum& self, const LocalMinimum& other) {
  return self.left_bound == other.left_bound &&
         self.right_bound == other.right_bound && self.y == other.y &&
         self.minimum_has_horizontal == other.minimum_has_horizontal;
}
}  // namespace wagyu
}  // namespace geometry
}  // namespace mapbox

PYBIND11_MAKE_OPAQUE(LocalMinimumList);

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of mapbox/wagyu library.
    )pbdoc";

  py::enum_<mapbox::geometry::wagyu::clip_type>(m, OPERATION_KIND_NAME)
      .value("INTERSECTION", mapbox::geometry::wagyu::clip_type_intersection)
      .value("UNION", mapbox::geometry::wagyu::clip_type_union)
      .value("DIFFERENCE", mapbox::geometry::wagyu::clip_type_difference)
      .value("XOR", mapbox::geometry::wagyu::clip_type_x_or);

  py::enum_<mapbox::geometry::wagyu::edge_side>(m, EDGE_SIDE_NAME)
      .value("LEFT", mapbox::geometry::wagyu::edge_left)
      .value("RIGHT", mapbox::geometry::wagyu::edge_right);

  py::enum_<mapbox::geometry::wagyu::fill_type>(m, FILL_KIND_NAME)
      .value("EVEN_ODD", mapbox::geometry::wagyu::fill_type_even_odd)
      .value("NON_ZERO", mapbox::geometry::wagyu::fill_type_non_zero)
      .value("POSITIVE", mapbox::geometry::wagyu::fill_type_positive)
      .value("NEGATIVE", mapbox::geometry::wagyu::fill_type_negative);

  py::enum_<mapbox::geometry::wagyu::polygon_type>(m, POLYGON_KIND_NAME)
      .value("SUBJECT", mapbox::geometry::wagyu::polygon_type_subject)
      .value("CLIP", mapbox::geometry::wagyu::polygon_type_clip);

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
      .def_readonly("y", &Point::y);

  py::class_<LinearRing>(m, LINEAR_RING_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<Point>&>())
      .def(py::self == py::self)
      .def("__repr__", repr<LinearRing>)
      .def("__len__", to_size<LinearRing>)
      .def("__getitem__", to_item<LinearRing>, py::arg("index"))
      .def("__iter__", to_iterator<LinearRing>, py::keep_alive<0, 1>());

  py::class_<Polygon>(m, POLYGON_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<LinearRing>&>())
      .def(py::self == py::self)
      .def("__repr__", repr<Polygon>)
      .def("__len__", to_size<Polygon>)
      .def("__getitem__", to_item<Polygon>, py::arg("index"))
      .def("__iter__", to_iterator<Polygon>, py::keep_alive<0, 1>());

  py::class_<Multipolygon>(m, MULTIPOLYGON_NAME)
      .def(py::init<>())
      .def(py::init<const std::vector<Polygon>&>())
      .def(py::self == py::self)
      .def("__repr__", repr<Multipolygon>)
      .def("__len__", to_size<Multipolygon>)
      .def("__getitem__", to_item<Multipolygon>, py::arg("index"))
      .def("__iter__", to_iterator<Multipolygon>, py::keep_alive<0, 1>());

  py::class_<PointNode, std::unique_ptr<PointNode, py::nodelete>>(
      m, POINT_NODE_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::self == py::self)
      .def("__repr__", repr<PointNode>)
      .def_readonly("x", &PointNode::x)
      .def_readonly("y", &PointNode::y)
      .def_readwrite("next", &PointNode::next)
      .def_readwrite("prev", &PointNode::prev)
      .def("reverse", &mapbox::geometry::wagyu::reverse_ring<coordinate_t>);

  py::class_<Box>(m, BOX_NAME)
      .def(py::init<Point, Point>(), py::arg("min"), py::arg("max"))
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
      .def_readonly("min", &Box::min)
      .def_readonly("max", &Box::max);

  py::class_<Edge>(m, EDGE_NAME)
      .def(py::init<Point, Point>(), py::arg("start"), py::arg("end"))
      .def(py::pickle(
          [](const Edge& self) {  // __getstate__
            return py::make_tuple(self.bot, self.top);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Edge(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Edge>)
      .def_readonly("bottom", &Edge::bot)
      .def_readonly("top", &Edge::top)
      .def_readonly("dx", &Edge::dx);

  py::class_<Ring, std::unique_ptr<Ring, py::nodelete>>(m, RING_NAME)
      .def(py::init<std::size_t, const RingVector&, PointNodePtr, PointNodePtr,
                    bool>(),
           py::arg("index") = 0, py::arg("children") = RingVector{},
           py::arg("node").none(true) = nullptr,
           py::arg("bottom_node").none(true) = nullptr,
           py::arg("corrected") = false)
      .def(py::self == py::self)
      .def("__repr__", repr<Ring>)
      .def_readonly("index", &Ring::ring_index)
      .def_readonly("box", &Ring::bbox)
      .def_readonly("parent", &Ring::parent)
      .def_readonly("children", &Ring::children)
      .def_readonly("node", &Ring::points)
      .def_readonly("bottom_node", &Ring::bottom_point)
      .def_readonly("corrected", &Ring::corrected)
      .def_property_readonly("size", &Ring::size)
      .def_property_readonly("area", &Ring::area)
      .def_property_readonly("is_hole", &Ring::is_hole)
      .def_property_readonly("depth",
                             &mapbox::geometry::wagyu::ring_depth<coordinate_t>)
      .def("recalculate_stats", &Ring::recalculate_stats)
      .def("reset_stats", &Ring::reset_stats)
      .def("set_stats", &Ring::set_stats, py::arg("area"), py::arg("size"),
           py::arg("box"));

  py::class_<Bound, std::unique_ptr<Bound, py::nodelete>>(m, BOUND_NAME)
      .def(py::init<>())
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
      .def_readonly("side", &Bound::side);

  py::class_<LocalMinimum>(m, LOCAL_MINIMUM_NAME)
      .def(py::self == py::self)
      .def("__repr__", repr<LocalMinimum>)
      .def_readonly("left_bound", &LocalMinimum::left_bound)
      .def_readonly("right_bound", &LocalMinimum::right_bound)
      .def_readonly("y", &LocalMinimum::y)
      .def_readonly("minimum_has_horizontal",
                    &LocalMinimum::minimum_has_horizontal);

  py::class_<LocalMinimumList>(m, LOCAL_MINIMUM_LIST_NAME)
      .def(py::init<>())
      .def(py::self == py::self)
      .def("__repr__", repr<LocalMinimumList>)
      .def("__len__", to_size<LocalMinimumList>)
      .def("__getitem__", to_item<LocalMinimumList>, py::arg("index"),
           py::return_value_policy::reference)
      .def("__iter__", to_iterator<LocalMinimumList>, py::keep_alive<0, 1>())
      .def("add_linear_ring",
           [](LocalMinimumList& self, const LinearRing& ring,
              mapbox::geometry::wagyu::polygon_type polygon_kind) {
             return mapbox::geometry::wagyu::add_linear_ring(ring, self,
                                                             polygon_kind);
           });

  py::class_<Wagyu>(m, WAGYU_NAME)
      .def(py::init<>())
      .def("add_linear_ring", &Wagyu::add_ring<coordinate_t>)
      .def("add_polygon", &Wagyu::add_polygon<coordinate_t>)
      .def("clear", &Wagyu::clear)
      .def(
          "intersect",
          [](Wagyu& self,
             mapbox::geometry::wagyu::fill_type subject_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd,
             mapbox::geometry::wagyu::fill_type clip_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(mapbox::geometry::wagyu::clip_type_intersection,
                         solution, subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd,
          py::arg("clip_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd)
      .def(
          "subtract",
          [](Wagyu& self,
             mapbox::geometry::wagyu::fill_type subject_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd,
             mapbox::geometry::wagyu::fill_type clip_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(mapbox::geometry::wagyu::clip_type_difference,
                         solution, subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd,
          py::arg("clip_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd)
      .def(
          "unite",
          [](Wagyu& self,
             mapbox::geometry::wagyu::fill_type subject_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd,
             mapbox::geometry::wagyu::fill_type clip_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(mapbox::geometry::wagyu::clip_type_union, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd,
          py::arg("clip_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd)
      .def(
          "symmetric_subtract",
          [](Wagyu& self,
             mapbox::geometry::wagyu::fill_type subject_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd,
             mapbox::geometry::wagyu::fill_type clip_fill_kind =
                 mapbox::geometry::wagyu::fill_type_even_odd) {
            Multipolygon solution;
            self.execute(mapbox::geometry::wagyu::clip_type_x_or, solution,
                         subject_fill_kind, clip_fill_kind);
            return solution;
          },
          py::arg("subject_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd,
          py::arg("clip_fill_kind") =
              mapbox::geometry::wagyu::fill_type_even_odd)
      .def_property_readonly("bounds", &Wagyu::get_bounds)
      .def_readonly("minimums", &Wagyu::minima_list)
      .def_readonly("reverse_output", &Wagyu::reverse_output);

  py::class_<RingManager>(m, RING_MANAGER_NAME)
      .def(py::init<>())
      .def("__repr__", repr<RingManager>)
      .def_readonly("all_points", &RingManager::all_points)
      .def_readonly("hot_pixels", &RingManager::hot_pixels)
      .def_readonly("children", &RingManager::children)
      .def_readonly("rings", &RingManager::rings)
      .def_readonly("storage", &RingManager::storage)
      .def_readonly("index", &RingManager::index)
      .def("create_ring",
           &mapbox::geometry::wagyu::create_new_ring<coordinate_t>)
      .def(
          "create_new_point",
          [](RingManager& self, RingPtr ring, const Point& point) {
            return mapbox::geometry::wagyu::create_new_point<coordinate_t>(
                ring, point, self);
          },
          py::arg("ring"), py::arg("point"))
      .def(
          "create_new_point_after_node",
          [](RingManager& self, RingPtr ring, PointNodePtr node,
             const Point& point) {
            return mapbox::geometry::wagyu::create_new_point<coordinate_t>(
                ring, point, node, self);
          },
          py::arg("ring"), py::arg("node"), py::arg("point"))
      .def(
          "assign_as_child",
          [](RingManager& manager, RingPtr ring, RingPtr parent) {
            mapbox::geometry::wagyu::assign_as_child<coordinate_t>(ring, parent,
                                                                   manager);
          },
          py::arg("ring").none(false), py::arg("parent").none(true))
      .def(
          "reassign_as_child",
          [](RingManager& manager, RingPtr ring, RingPtr parent) {
            mapbox::geometry::wagyu::reassign_as_child<coordinate_t>(
                ring, parent, manager);
          },
          py::arg("ring").none(false), py::arg("parent").none(true))
      .def(
          "assign_as_sibling",
          [](RingManager& manager, RingPtr ring, RingPtr sibling) {
            mapbox::geometry::wagyu::assign_as_sibling<coordinate_t>(
                ring, sibling, manager);
          },
          py::arg("ring").none(false), py::arg("sibling").none(false))
      .def(
          "reassign_as_sibling",
          [](RingManager& manager, RingPtr ring, RingPtr sibling) {
            mapbox::geometry::wagyu::reassign_as_sibling<coordinate_t>(
                ring, sibling, manager);
          },
          py::arg("ring").none(false), py::arg("sibling").none(false))
      .def(
          "replace_ring",
          [](RingManager& manager, RingPtr original, RingPtr replacement) {
            mapbox::geometry::wagyu::ring1_replaces_ring2<coordinate_t>(
                replacement, original, manager);
          },
          py::arg("original").none(false), py::arg("replacment").none(false))
      .def(
          "remove_ring_and_points",
          [](RingManager& manager, RingPtr ring, bool remove_children = true,
             bool remove_from_parent = true) {
            mapbox::geometry::wagyu::remove_ring_and_points<coordinate_t>(
                ring, manager, remove_children, remove_from_parent);
          },
          py::arg("ring").none(false), py::arg("remove_children") = true,
          py::arg("remove_from_parent") = true)
      .def(
          "remove_ring",
          [](RingManager& manager, RingPtr ring, bool remove_children = true,
             bool remove_from_parent = true) {
            mapbox::geometry::wagyu::remove_ring<coordinate_t>(
                ring, manager, remove_children, remove_from_parent);
          },
          py::arg("ring").none(false), py::arg("remove_children") = true,
          py::arg("remove_from_parent") = true);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
