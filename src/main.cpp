#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <mapbox/geometry/box.hpp>
#include <mapbox/geometry/point.hpp>
#include <mapbox/geometry/wagyu/config.hpp>
#include <mapbox/geometry/wagyu/edge.hpp>
#include <mapbox/geometry/wagyu/point.hpp>
#include <mapbox/geometry/wagyu/ring.hpp>
#include <sstream>

namespace py = pybind11;

#define MODULE_NAME _wagyu
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define BOX_NAME "Box"
#define EDGE_NAME "Edge"
#define FILL_KIND_NAME "FillKind"
#define OPERATION_KIND_NAME "OperationKind"
#define POINT_NAME "Point"
#define POINT_NODE_NAME "PointNode"
#define POLYGON_KIND_NAME "PolygonKind"
#define RING_NAME "Ring"
#define RING_MANAGER_NAME "RingManager"

using coordinate_t = double;
using Box = mapbox::geometry::box<coordinate_t>;
using Edge = mapbox::geometry::wagyu::edge<coordinate_t>;
using Point = mapbox::geometry::point<coordinate_t>;
using PointNode = mapbox::geometry::wagyu::point<coordinate_t>;
using PointNodePtr = mapbox::geometry::wagyu::point_ptr<coordinate_t>;
using Ring = mapbox::geometry::wagyu::ring<coordinate_t>;
using RingPtr = mapbox::geometry::wagyu::ring_ptr<coordinate_t>;
using RingVector = mapbox::geometry::wagyu::ring_vector<coordinate_t>;
using RingManager = mapbox::geometry::wagyu::ring_manager<coordinate_t>;

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

template <class Object>
std::string repr(const Object& object) {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<double>::digits10 + 2);
  stream << object;
  return stream.str();
}

template <class Object>
static void write_maybe(std::ostream& stream, Object* value) {
  if (value == nullptr)
    stream << py::none();
  else
    stream << *value;
}

template <class Object>
static bool maybe_equal(Object* left, Object* right) {
  return left == nullptr ? right == nullptr
                         : right != nullptr && *left == *right;
}

template <class Object>
static bool vectors_equal(std::vector<Object*> left,
                          std::vector<Object*> right) {
  if (left.size() != right.size()) return false;
  auto size = left.size();
  for (std::size_t index = 0; index < size; ++index)
    if (!maybe_equal(left[index], right[index])) return false;
  return true;
}

template <typename Object>
static void write_vector(std::ostream& stream,
                         const std::vector<Object*>& elements) {
  stream << "[";
  if (!elements.empty()) {
    write_maybe(stream, elements[0]);
    std::for_each(std::next(std::begin(elements)), std::end(elements),
                  [&stream](Object* value) {
                    stream << ", ";
                    write_maybe(stream, value);
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

static std::ostream& operator<<(std::ostream& stream, const polygon_type& type) {
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
  write_vector(stream, ring.children);
  stream << ", ";
  write_maybe(stream, ring.points);
  stream << ", ";
  write_maybe(stream, ring.bottom_point);
  stream << ", " << bool_repr(ring.corrected) << ")";
  return stream;
}

static std::ostream& operator<<(std::ostream& stream, const RingManager& manager) {
  return stream << C_STR(MODULE_NAME) "." RING_MANAGER_NAME "()";
}

static std::ostream& operator<<(std::ostream& stream, const Edge& edge) {
  return stream << C_STR(MODULE_NAME) "." EDGE_NAME "(" << edge.bot << ", "
                << edge.top << ")";
}

static bool operator==(const Edge& left, const Edge& right) {
  return left.bot == right.bot && left.top == right.top;
}

static bool operator==(const Ring& left, const Ring& right) {
  return left.ring_index == right.ring_index &&
         vectors_equal(left.children, right.children) &&
         maybe_equal(left.points, right.points) &&
         maybe_equal(left.bottom_point, right.bottom_point) &&
         left.corrected == right.corrected;
}
}  // namespace wagyu
}  // namespace geometry
}  // namespace mapbox

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of mapbox/wagyu library.
    )pbdoc";

  py::enum_<mapbox::geometry::wagyu::clip_type>(m, OPERATION_KIND_NAME)
      .value("INTERSECTION", mapbox::geometry::wagyu::clip_type_intersection)
      .value("UNION", mapbox::geometry::wagyu::clip_type_union)
      .value("DIFFERENCE", mapbox::geometry::wagyu::clip_type_difference)
      .value("XOR", mapbox::geometry::wagyu::clip_type_x_or);

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
